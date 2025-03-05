const fs = require('fs');
const path = require('path');
const acorn = require('acorn');
const walk = require('acorn-walk');

/**
 * Dependency analyzer that scans the codebase and identifies module dependencies
 * including potential circular dependencies
 */
class DependencyAnalyzer {
  constructor(rootDir) {
    this.rootDir = rootDir;
    this.dependencies = new Map(); // Module -> Set of dependencies
    this.fileToModule = new Map(); // File path -> Module name
  }

  /**
   * Scan the project to build dependency graph
   */
  async scan() {
    console.log('Starting dependency scan...');
    await this.scanDirectory(this.rootDir);
    return this.dependencies;
  }

  /**
   * Recursively scan directories to find JS/TS files
   */
  async scanDirectory(dir) {
    const files = fs.readdirSync(dir);
    
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory() && !this.shouldIgnoreDir(file)) {
        await this.scanDirectory(fullPath);
      } else if (this.isJsOrTs(file)) {
        await this.analyzeFile(fullPath);
      }
    }
  }

  /**
   * Analyze a single file to extract its imports
   */
  async analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const moduleName = this.getModuleName(filePath);
      this.fileToModule.set(filePath, moduleName);
      
      if (!this.dependencies.has(moduleName)) {
        this.dependencies.set(moduleName, new Set());
      }
      
      // Parse the file and extract imports
      const ast = acorn.parse(content, {
        sourceType: 'module',
        ecmaVersion: 2020,
      });
      
      walk.simple(ast, {
        ImportDeclaration: (node) => {
          const importPath = node.source.value;
          const importedModule = this.resolveImportToModule(importPath, filePath);
          
          if (importedModule && importedModule !== moduleName) {
            this.dependencies.get(moduleName).add(importedModule);
          }
        },
        CallExpression: (node) => {
          // Handle require() calls
          if (node.callee.name === 'require' && node.arguments.length > 0 && node.arguments[0].type === 'Literal') {
            const importPath = node.arguments[0].value;
            const importedModule = this.resolveImportToModule(importPath, filePath);
            
            if (importedModule && importedModule !== moduleName) {
              this.dependencies.get(moduleName).add(importedModule);
            }
          }
        }
      });
    } catch (error) {
      console.error(`Error analyzing file ${filePath}:`, error.message);
    }
  }

  /**
   * Find circular dependencies in the dependency graph
   * @returns {Array} Array of circular dependency paths
   */
  findCircularDependencies() {
    const visited = new Set();
    const recursionStack = new Set();
    const circularDependencies = [];
    
    const dfs = (module, path = []) => {
      if (recursionStack.has(module)) {
        const cycleStart = path.indexOf(module);
        circularDependencies.push(path.slice(cycleStart).concat(module));
        return;
      }
      
      if (visited.has(module)) return;
      
      visited.add(module);
      recursionStack.add(module);
      path.push(module);
      
      const deps = this.dependencies.get(module) || new Set();
      for (const dep of deps) {
        dfs(dep, [...path]);
      }
      
      recursionStack.delete(module);
    };
    
    for (const module of this.dependencies.keys()) {
      if (!visited.has(module)) {
        dfs(module);
      }
    }
    
    return circularDependencies;
  }
  
  /**
   * Generate a detailed report of dependencies and circular dependencies
   */
  generateReport() {
    const circles = this.findCircularDependencies();
    
    return {
      totalModules: this.dependencies.size,
      moduleCount: this.dependencies.size,
      dependencies: Object.fromEntries(
        [...this.dependencies.entries()].map(([key, value]) => [key, [...value]])
      ),
      circularDependencies: circles,
      circularDependencyCount: circles.length,
    };
  }
  
  /**
   * Export dependency graph to a format suitable for visualization
   */
  exportDependencyGraph() {
    const nodes = [];
    const links = [];
    
    let i = 0;
    const nodeIndices = {};
    
    for (const module of this.dependencies.keys()) {
      nodeIndices[module] = i++;
      nodes.push({ id: module, group: this.getModuleGroup(module) });
    }
    
    for (const [source, targets] of this.dependencies.entries()) {
      for (const target of targets) {
        links.push({
          source: nodeIndices[source],
          target: nodeIndices[target],
          value: 1
        });
      }
    }
    
    return { nodes, links };
  }
  
  // Helper methods
  isJsOrTs(file) {
    return /\.(js|jsx|ts|tsx)$/.test(file);
  }
  
  shouldIgnoreDir(dir) {
    return ['node_modules', 'dist', 'build', '.git'].includes(dir);
  }
  
  getModuleName(filePath) {
    // Convert file path to module name
    // This is a simple implementation - you might need to adjust based on project structure
    const relativePath = path.relative(this.rootDir, filePath);
    const dirName = path.dirname(relativePath);
    
    if (dirName === '.') {
      return path.basename(filePath, path.extname(filePath));
    }
    
    // Get module name from directory structure
    return dirName.split(path.sep)[0];
  }
  
  resolveImportToModule(importPath, currentFilePath) {
    // Convert import path to module name
    if (importPath.startsWith('.')) {
      // Relative import
      const absolutePath = path.resolve(path.dirname(currentFilePath), importPath);
      const dirPath = path.extname(absolutePath) ? path.dirname(absolutePath) : absolutePath;
      return path.relative(this.rootDir, dirPath).split(path.sep)[0];
    } else {
      // Package import
      return importPath.split('/')[0];
    }
  }
  
  getModuleGroup(moduleName) {
    // Group modules by their top-level directory
    // This is useful for visualization
    const parts = moduleName.split(path.sep);
    return parts[0];
  }
}

module.exports = DependencyAnalyzer;
