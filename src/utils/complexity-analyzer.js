const fs = require('fs');
const path = require('path');
const esprima = require('esprima');
const escomplex = require('escomplex');
const chalk = require('chalk');

/**
 * Code Complexity Analyzer
 * Analyzes JavaScript/TypeScript code for various complexity metrics
 */
class ComplexityAnalyzer {
  constructor(config = {}) {
    this.config = {
      thresholds: {
        cyclomaticComplexity: config.thresholds?.cyclomaticComplexity || 10,
        maintainabilityIndex: config.thresholds?.maintainabilityIndex || 65,
        halsteadDifficulty: config.thresholds?.halsteadDifficulty || 15,
        parameterCount: config.thresholds?.parameterCount || 5,
      },
      ignorePatterns: config.ignorePatterns || [/node_modules/, /\.test\./, /\.spec\./],
      reportFormat: config.reportFormat || 'detailed'
    };
  }

  /**
   * Analyzes a single file for complexity metrics
   * @param {string} filePath - Path to the file to analyze
   * @returns {Object} Complexity metrics for the file
   */
  analyzeFile(filePath) {
    try {
      const code = fs.readFileSync(filePath, 'utf-8');
      const ast = esprima.parse(code, { loc: true, jsx: true });
      const result = escomplex.analyse(ast);
      
      // Augment the result with file information
      result.filePath = filePath;
      result.fileName = path.basename(filePath);
      
      return this.processAnalysisResult(result);
    } catch (error) {
      console.error(`Error analyzing file ${filePath}:`, error.message);
      return {
        filePath,
        fileName: path.basename(filePath),
        error: error.message,
        isProblematic: true,
        metrics: {}
      };
    }
  }

  /**
   * Analyzes a directory recursively
   * @param {string} directoryPath - Path to the directory to analyze
   * @returns {Array} Array of analysis results for each file
   */
  analyzeDirectory(directoryPath) {
    const results = [];
    
    const processDir = (dirPath) => {
      const files = fs.readdirSync(dirPath);
      
      files.forEach(file => {
        const fullPath = path.join(dirPath, file);
        const stats = fs.statSync(fullPath);
        
        if (stats.isDirectory()) {
          processDir(fullPath);
        } else if (this.isJavaScriptFile(fullPath) && !this.isIgnored(fullPath)) {
          results.push(this.analyzeFile(fullPath));
        }
      });
    };
    
    processDir(directoryPath);
    return results;
  }
  
  /**
   * Processes raw analysis results and adds derived metrics
   * @param {Object} result - Raw analysis result
   * @returns {Object} Enhanced analysis result with problem indicators
   */
  processAnalysisResult(result) {
    const metrics = {
      cyclomaticComplexity: result.aggregate.cyclomatic,
      maintainabilityIndex: result.maintainabilityIndex || this.calculateMaintainabilityIndex(result),
      halsteadDifficulty: result.aggregate.halstead.difficulty,
      lineCount: result.aggregate.sloc.logical,
      parameterCount: this.getMaxParameterCount(result),
      functionCount: result.functions.length
    };
    
    const problems = [];
    
    if (metrics.cyclomaticComplexity > this.config.thresholds.cyclomaticComplexity) {
      problems.push({
        type: 'cyclomaticComplexity',
        value: metrics.cyclomaticComplexity,
        threshold: this.config.thresholds.cyclomaticComplexity,
        message: `High cyclomatic complexity (${metrics.cyclomaticComplexity} > ${this.config.thresholds.cyclomaticComplexity})`
      });
    }
    
    if (metrics.maintainabilityIndex < this.config.thresholds.maintainabilityIndex) {
      problems.push({
        type: 'maintainabilityIndex',
        value: metrics.maintainabilityIndex,
        threshold: this.config.thresholds.maintainabilityIndex,
        message: `Low maintainability index (${metrics.maintainabilityIndex} < ${this.config.thresholds.maintainabilityIndex})`
      });
    }
    
    // Find problematic functions with high complexity
    const complexFunctions = result.functions
      .filter(fn => fn.cyclomatic > this.config.thresholds.cyclomaticComplexity)
      .map(fn => ({
        name: fn.name || '(anonymous)',
        complexity: fn.cyclomatic,
        line: fn.line,
        threshold: this.config.thresholds.cyclomaticComplexity
      }));
    
    return {
      filePath: result.filePath,
      fileName: result.fileName,
      metrics,
      problems,
      complexFunctions,
      isProblematic: problems.length > 0 || complexFunctions.length > 0
    };
  }
  
  /**
   * Calculates maintainability index based on other metrics
   * @param {Object} result - Analysis result
   * @returns {number} Maintainability index (0-100)
   */
  calculateMaintainabilityIndex(result) {
    const HV = result.aggregate.halstead.volume;
    const CC = result.aggregate.cyclomatic;
    const SLOC = result.aggregate.sloc.logical;
    
    // Standard maintainability index formula
    const MI = Math.max(0, (171 - 5.2 * Math.log(HV) - 0.23 * CC - 16.2 * Math.log(SLOC)) * 100 / 171);
    return Math.round(MI);
  }
  
  /**
   * Gets the maximum parameter count for any function
   * @param {Object} result - Analysis result
   * @returns {number} Maximum parameter count
   */
  getMaxParameterCount(result) {
    let maxCount = 0;
    
    if (result.functions && result.functions.length > 0) {
      maxCount = Math.max(...result.functions.map(fn => fn.params || 0));
    }
    
    return maxCount;
  }
  
  /**
   * Checks if a file is a JavaScript or TypeScript file
   * @param {string} filePath - Path to check
   * @returns {boolean} Whether the file is JS/TS
   */
  isJavaScriptFile(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    return ['.js', '.jsx', '.ts', '.tsx'].includes(ext);
  }
  
  /**
   * Checks if a file should be ignored based on ignore patterns
   * @param {string} filePath - Path to check
   * @returns {boolean} Whether the file should be ignored
   */
  isIgnored(filePath) {
    return this.config.ignorePatterns.some(pattern => 
      pattern instanceof RegExp ? pattern.test(filePath) : filePath.includes(pattern)
    );
  }
  
  /**
   * Generates a formatted report of analysis results
   * @param {Array} results - Analysis results
   * @returns {string} Formatted report
   */
  generateReport(results) {
    const problematicFiles = results.filter(r => r.isProblematic);
    
    if (this.config.reportFormat === 'json') {
      return JSON.stringify(problematicFiles, null, 2);
    }
    
    let report = '\n' + chalk.bold('CODE COMPLEXITY ANALYSIS REPORT') + '\n\n';
    
    if (problematicFiles.length === 0) {
      report += chalk.green('✓ No complexity issues found.\n');
      return report;
    }
    
    report += chalk.yellow(`Found ${problematicFiles.length} file(s) with complexity issues:\n\n`);
    
    problematicFiles.forEach(file => {
      report += chalk.bold(file.filePath) + '\n';
      
      file.problems.forEach(problem => {
        report += `  ${chalk.red('✗')} ${problem.message}\n`;
      });
      
      if (file.complexFunctions.length > 0) {
        report += `  ${chalk.yellow('⚠')} Complex functions:\n`;
        file.complexFunctions.forEach(fn => {
          report += `    - ${fn.name} (line ${fn.line}): complexity ${fn.complexity} > ${fn.threshold}\n`;
        });
      }
      
      report += `  Metrics: CC=${file.metrics.cyclomaticComplexity}, MI=${file.metrics.maintainabilityIndex}, Functions=${file.metrics.functionCount}\n\n`;
    });
    
    return report;
  }
}

module.exports = ComplexityAnalyzer;
