const logger = require("./unifiedLogger");
const axios = require("axios");
const fs = require("fs").promises;
const path = require("path");
const { promisify } = require('util');
const exec = promisify(require('child_process').exec);

// Common patterns for code scanning
const COMMON_ISSUES = {
  javascript: {
    security: [
      { pattern: /eval\s*\(/g, message: "Potential security risk: eval() usage" },
      { pattern: /innerText\s*=/g, message: "Consider using textContent instead of innerText" },
      { pattern: /localStorage\s*\.\s*(set|get)Item/g, message: "Consider validating localStorage data" }
    ],
    quality: [
      { pattern: /console\.(log|debug|info)/g, message: "Remove console statements in production" },
      { pattern: /\/\/ TODO/g, message: "Unresolved TODO comment" },
      { pattern: /function\s*\([^\)]{30,}\)/g, message: "Function has too many parameters" }
    ],
    performance: [
      { pattern: /\.forEach\s*\(/g, message: "Consider using for...of for better performance" },
      { pattern: /document\.querySelectorAll/g, message: "Cache DOM queries for better performance" },
      { pattern: /\.push\s*\([^\)]*\)\s*;\s*.*\.push/g, message: "Multiple array pushes could be combined" }
    ]
  },
  python: {
    security: [
      { pattern: /exec\s*\(/g, message: "Potential security risk: exec() usage" },
      { pattern: /input\s*\(/g, message: "Validate input() data in production" },
      { pattern: /import\s+os(?!\S)/g, message: "Sensitive OS operations should be sandboxed" }
    ],
    quality: [
      { pattern: /print\s*\(/g, message: "Remove print statements in production" },
      { pattern: /#\s*TODO/g, message: "Unresolved TODO comment" },
      { pattern: /def\s+[^(]+\([^\)]{30,}\)/g, message: "Function has too many parameters" }
    ],
    performance: [
      { pattern: /\[[^\]]+for[^\]]+in[^\]]+\]/g, message: "Consider optimizing list comprehension" },
      { pattern: /\.count\s*\([^\)]*\)\s*>\s*0/g, message: "Replace count() > 0 with item in list" },
      { pattern: /open\s*\([^)]*\)/g, message: "Ensure files are properly closed with context manager" }
    ]
  }
};

class AgentOrchestrator {
  constructor(config = {}) {
    this.agents = new Map();;
    this.cache = new Map();s.cache = new Map();
    this.activeTasks = new Set();
    this.pendingTasks = [];
    this.maxConcurrent = config.maxConcurrent || 4;
    this.cacheAge = config.cacheAge || 30 * 60 * 1000; // 30 minutes
    this.serviceUrl = config.serviceUrl || null;
    this.lastCacheCleanup = Date.now();
    this.cacheCleanupInterval = setInterval(
      () => this.cleanupCache(),
      5 * 60 * 1000000000
    );
  }

  async executeTask(agentName, params) {
    if (this.activeTasks.size >= this.maxConcurrent) {
      return new Promise((resolve, reject) => {
        this.pendingTasks.push({ agentName, params, resolve, reject });
        logger.debug(
          `Task queued: ${agentName} (${this.pendingTasks.length} pending)`ks.length} pending)`ks.length} pending)`
        );
      });
    }

    const taskId = `${agentName}-${Date.now()}-${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    this.activeTasks.add(taskId);

    try {
      const cacheKey = this.getCacheKey(agentName, params);
      if (cacheKey && this.cache.has(cacheKey)) {
        const cachedResult = this.cache.get(cacheKey);
        if (Date.now() - cachedResult.timestamp < this.cacheAge) {
          logger.debug(`Cache hit for ${agentName}`);
          return cachedResult.result;
        } else {
          this.cache.delete(cacheKey);
        }
      }

      const agent = this.agents.get(agentName);
      if (!agent) {
        throw new Error(`Agent not found: ${agentName}`);
      }

      agent.status = "busy";
      agent.lastRun = Date.now();

      let result;
      const startTime = Date.now();

      try {
        if (this.serviceUrl && (agent.options.useRemote || !agent.handler)) {
          logger.debug(`Executing ${agentName} via remote service`);
          result = await this.executeRemoteTask(
            agentName,
            params,
            agent.options.timeout
          );
        } else {
          logger.debug(`Executing ${agentName} locally`);
          result = await agent.handler(params);
        }

        const executionTime = Date.now() - startTime;
        agent.successCount++;
        const totalRuns = agent.successCount + agent.errorCount;
        agent.avgExecutionTime =
          (agent.avgExecutionTime * (totalRuns - 1) + executionTime) /
          totalRuns;

        if (cacheKey) {
          this.cache.set(cacheKey, {
            result,
            timestamp: Date.now(),
          });
        }

        return result;
      } catch (error) {
        agent.errorCount++;
        throw error;
      } finally {
        agent.status = "idle";
      }
    } catch (error) {
      logger.error(`Failed to execute task ${agentName}: ${error.message}`);
      throw error;
    } finally {
      this.activeTasks.delete(taskId);
      this.processNextPendingTask();
    }
  }

  async executeRemoteTask(
    agentName,
    params,
    timeout,
    retries = 3,
    delay = 1000
  ) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await axios.post(
          this.serviceUrl,
          {
            agent_name: agentName,
            params: params,
          },
          {
            timeout: timeout,
            headers: { "Content-Type": "application/json" },
          }
        );
        return response.data.result;
      } catch (error) {
        if (attempt < retries) {
          logger.warn(
            `Attempt ${attempt} failed for ${agentName}, retrying in ${delay}ms: ${error.message}`
          );
          await new Promise((resolve) => setTimeout(resolve, delay));
          delay *= 2; // Exponential backoff
        } else {
          logger.error(
            `All attempts failed for ${agentName}: ${error.message}`
          );
          throw error;
        }
      }
    }
  }

  processNextPendingTask() {
    if (
      this.pendingTasks.length > 0 &&
      this.activeTasks.size < this.maxConcurrent
    ) {
      const { agentName, params, resolve, reject } = this.pendingTasks.shift();
      this.executeTask(agentName, params).then(resolve).catch(reject);
    }
  }

  getCacheKey(agentName, params) {
    const agent = this.agents.get(agentName);
    // Only cache if the agent is configured to use caching
    if (!agent || agent.options.noCache) return null;

    try {
  getCacheKey(agentName, params) {
    const agent = this.agents.get(agentName);
    // Only cache if the agent is configured to use caching
    if (!agent || agent.options.noCache) return null;

    try {
      return `${agentName}-${JSON.stringify(params)}`;
    } catch (e) {
      logger.warn(
        `Could not generate cache key for ${agentName}: ${e.message}`
      );
      return null;
    }
  }

  /**
   * Clean up expired cache entries
   */
  cleanupCache() {
    const now = Date.now();
    let expiredCount = 0;
    for (const [key, value] of this.cache.entries()) {for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.cacheAge) {
        this.cache.delete(key);
        expiredCount++;
      }
    }

    if (expiredCount > 0) {    if (expiredCount > 0) {
      logger.debug(`Cleaned up ${expiredCount} expired cache entries`);
    }
    this.lastCacheCleanup = now;p = now;
  }

  /**
   * Clear the cache for a specific agent or all agents   * Clear the cache for a specific agent or all agents
   */
  clearCache(agentName = null) {
    if (agentName) {
      // Clear cache for specific agent
      const prefix = `${agentName}-`;
      let count = 0;
      for (const key of this.cache.keys()) {
        if (key.startsWith(prefix)) {
          this.cache.delete(key);
          count++;
        }
      }
      logger.info(`Cleared ${count} cache entries for ${agentName}`);
    } else {
      // Clear all cache
      const count = this.cache.size;
      this.cache.clear();
      logger.info(`Cleared all ${count} cache entries`);
    }
  }

  /**
   * Get stats for all registered agents
   */
  getAgentStats() {
    const stats = {};
    for (const [name, agent] of this.agents.entries()) {
      stats[name] = {
        status: agent.status,
        lastRun: agent.lastRun,
        successCount: agent.successCount,
        errorCount: agent.errorCount,
        avgExecutionTime: agent.avgExecutionTime,
      };
    }
    return stats;
  }

  /**
   * Clean up resources when shutting down
   */
  destroy() {
    if (this.cacheCleanupInterval) {
      clearInterval(this.cacheCleanupInterval);
    }
    this.cache.clear();
    this.agents.clear();
    this.pendingTasks = [];
    this.activeTasks.clear();
  }
}

/**
 * Scans code files for potential issues
 */
async function scanCodeFunction(params) {
  const { files, patterns = COMMON_ISSUES, severity = "all" } = params;
  logger.info(`Scanning ${files.length} files for issues`);
  
  const results = [];
  let fileCount = 0;
  
  for (const file of files) {
    try {
      fileCount++;
      const content = await fs.readFile(file, 'utf-8');
      const extension = path.extname(file).toLowerCase();
      const language = extension === '.js' ? 'javascript' : 
                      extension === '.py' ? 'python' : 'other';
      
      if (language === 'other') {
        continue; // Skip unsupported file types
      }
      
      // Determine which pattern sets to use based on severity filter
      const patternSets = severity === 'all' 
        ? ['security', 'quality', 'performance']
        : [severity];
      
      // Scan the file using appropriate patterns
      patternSets.forEach(patternType => {
        if (!patterns[language][patternType]) return;
        
        patterns[language][patternType].forEach(({ pattern, message }) => {
          let match;
          while ((match = pattern.exec(content)) !== null) {
            const lineNumber = content.substring(0, match.index).split('\n').length;
            results.push({
              file,
              line: lineNumber,
              type: patternType,
              severity: patternType === 'security' ? 9 : 
                       patternType === 'quality' ? 6 : 4,
              message,
              context: extractContext(content, match.index)
            });
          }
        });
      });
      
      // Simple progress logging for large scans
      if (fileCount % 50 === 0) {
        logger.debug(`Scanned ${fileCount}/${files.length} files...`);
      }
    } catch (error) {
      logger.error(`Error scanning ${file}: ${error.message}`);
      results.push({
        file,
        type: 'error',
        severity: 8,
        message: `Error scanning file: ${error.message}`,
      });
    }
  }
  
  logger.info(`Completed scan of ${fileCount} files, found ${results.length} issues`);
  return results;
}

/**
 * Extract context around the match for better understanding
 */
function extractContext(content, index, contextSize = 100) {
  const start = Math.max(0, index - contextSize);
  const end = Math.min(content.length, index + contextSize);
  return content.substring(start, end);
}

/**
 * Analyzes runtime logs and errors for patterns and issues
 */
async function analyzeRuntimeFunction(params) {
  const { logs, error, context = {} } = params;
  logger.info(`Analyzing runtime information, ${logs?.length || 0} log entries`);
  
  const results = {
    patterns: [],
    recommendations: [],
    relatedCode: null
  };
  
  try {
    // If we have a specific error to analyze
    if (error) {
      // Extract the stack trace and parse for insights
      const stackTrace = error.stack || String(error);
      results.patterns.push({
        type: 'error',
        pattern: 'exception',
        message: error.message || 'Unknown error',
        stack: stackTrace,
        frequency: 1
      });
      
      // Look for file references in the stack trace
      const fileMatches = stackTrace.match(/\(([^:)]+):(\d+):(\d+)\)/g);
      if (fileMatches && fileMatches.length) {
        // Extract the most relevant file (usually the first one that's in our project)
        const filePath = fileMatches[0].replace(/[()]/g, '').split(':')[0];
        
        try {
          // Try to read the file to provide context
          const fileContent = await fs.readFile(filePath, 'utf-8');
          const lines = fileContent.split('\n');
          const errorLine = parseInt(fileMatches[0].split(':')[1]);
          
          // Get context around the error
          const startLine = Math.max(0, errorLine - 5);
          const endLine = Math.min(lines.length, errorLine + 5);
          const codeContext = lines.slice(startLine, endLine).join('\n');
          
          results.relatedCode = {
            file: filePath,
            line: errorLine,
            context: codeContext
          };
          
          // Generate recommendations based on common error patterns
          if (error.message?.includes('is not a function')) {
            results.recommendations.push({
              confidence: 0.8,
              suggestion: "Check if the variable type is correct before calling the method",
              example: `if (typeof x === 'function') { x(); }`
            });
          } else if (error.message?.includes('Cannot read property')) {
            results.recommendations.push({
              confidence: 0.9,
              suggestion: "Add null/undefined check before accessing properties",
              example: `if (obj && obj.property) { /* use obj.property */ }`
            });
          }
        } catch (fileError) {
          logger.warn(`Could not read file ${filePath}: ${fileError.message}`);
        }
      }
    }
    
    // Analyze log patterns if logs are provided
    if (logs && logs.length) {
      const patterns = {};
      
      // Look for patterns in logs
      logs.forEach(log => {
        // Look for common warning patterns
        if (log.level === 'warn' || log.message?.includes('Warning')) {
          const pattern = log.message?.substring(0, 50);
          if (pattern) {
            patterns[pattern] = (patterns[pattern] || 0) + 1;
          }
        }
        
        // Look for Deprecation warnings
        if (log.message?.includes('Deprecat')) {
          results.recommendations.push({
            confidence: 0.7,
            suggestion: `Update deprecated API usage in ${log.source || 'unknown location'}`,
            details: log.message
          });
        }
      });
      
      // Add recurring patterns to results
      for (const [pattern, count] of Object.entries(patterns)) {
        if (count > 1) {
          results.patterns.push({
            type: 'recurring',
            pattern,
            frequency: count
          });
        }
      }
    }
    
    return results;
  } catch (analyzeError) {
    logger.error(`Error during runtime analysis: ${analyzeError.message}`);
    return {
      error: analyzeError.message,
      patterns: [],
      recommendations: []
    };
  }
}

/**
 * Generates potential fixes for identified issues
 */
async function generateFixFunction(params) {
  const { code, issues } = params;
  logger.info(`Generating fixes for ${issues.length} issues`);
  
  const fixes = [];
  
  // For each issue, generate an appropriate fix
  for (const issue of issues) {
    try {
      // Handle simple cases with direct replacements
      if (issue.type === 'quality') {
        if (issue.message.includes('console.')) {
          fixes.push({
            file: issue.file,
            line: issue.line,
            original: issue.context,
            replacement: issue.context.replace(/console\.(log|debug|info)\([^;]*\);?/g, '/* Removed console statement */'),
            confidence: 0.9,
            description: "Removed console statement"
          });
        } 
        else if (issue.message.includes('TODO')) {
          fixes.push({
            file: issue.file,
            line: issue.line,
            confidence: 0.3,
            description: "TODO comments should be addressed or converted to tracked issues",
            requiresHumanReview: true
          });
        }
      }
      else if (issue.type === 'performance') {
        if (issue.message.includes('forEach')) {
          fixes.push({
            file: issue.file,
            line: issue.line,
            original: issue.context,
            replacement: issue.context.replace(
              /(\w+)\.forEach\s*\(\s*(\w+)\s*=>\s*\{([^}]+)\}\s*\)/g, 
              'for (const $2 of $1) {$3}'
            ),
            confidence: 0.7,
            description: "Converted .forEach() to for...of loop for better performance"
          });
        }
      }
      
      // For more complex cases, we'd normally use the AI service
      // In this local implementation, we'll create placeholder recommendations
      else if (issue.type === 'security') {
        fixes.push({
          file: issue.file,
          line: issue.line,
          confidence: 0.5,
          description: `Security issue requires careful review: ${issue.message}`,
          requiresHumanReview: true,
          suggestedApproach: "Consider safer alternatives that don't expose the application to injection risks"
        });
      }
    } catch (fixError) {
      logger.error(`Error generating fix for issue in ${issue.file}: ${fixError.message}`);
      fixes.push({
        file: issue.file,
        error: fixError.message,
        requiresHumanReview: true
      });
    }
  }
  
  return {
    fixes,
    summary: `Generated ${fixes.length} potential fixes for ${issues.length} issues`,
    automatedFixCount: fixes.filter(f => !f.requiresHumanReview).length
  };
}

/**
 * Gets all relevant code files from a directory
 */
async function getAllCodeFiles(directory = '.', extensions = ['.js', '.py', '.jsx', '.ts', '.tsx'], excludeDirs = ['node_modules', 'dist']) {
  try {
    const results = [];
    
    async function scanDir(dir) {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          if (!excludeDirs.includes(entry.name)) {
            await scanDir(fullPath);
          }
        } else if (extensions.includes(path.extname(entry.name).toLowerCase())) {
          results.push(fullPath);
        }
      }
    }
    
    await scanDir(directory);
    return results;
  } catch (error) {
    logger.error(`Error scanning directory for code files: ${error.message}`);
    return [];
  }
}

const debugOrchestrator = new AgentOrchestrator({
  serviceUrl: "http://localhost:8000/ai/debug",
});

// Register the core debugging agents
debugOrchestrator.registerAgent("CodeScanAgent", scanCodeFunction);
debugOrchestrator.registerAgent("RuntimeAnalyzer", analyzeRuntimeFunction);
debugOrchestrator.registerAgent("FixGenerator", generateFixFunction);

// Register the Debug Coordinator - the main entry point for the debug system
debugOrchestrator.registerAgent("DebugCoordinator", async (params) => {
  const { target = '.', depth = 'standard', focusAreas = ['security', 'quality', 'performance'] } = params;
  logger.info(`Starting coordinated debug scan of ${target}, depth: ${depth}`);
  
  const results = {
    issues: [],
    suggestions: [],
    fixes: [],
    scanTime: Date.now()
  };
  
  try {
    // Step 1: Gather all relevant files
    const files = Array.isArray(target) ? target : await getAllCodeFiles(target);
    logger.info(`Found ${files.length} files to analyze`);
    
    // Step 2: Determine scan depth and allocate resources accordingly
    const batchSize = depth === 'quick' ? 100 : depth === 'thorough' ? 20 : 50;
    
    // Step 3: Process files in batches to avoid overloading the system
    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize);
      const batchIssues = await debugOrchestrator.executeTask("CodeScanAgent", { 
        files: batch,
        severity: focusAreas
      });
      
      results.issues.push(...batchIssues);
      
      // Log progress for large scans
      logger.debug(`Processed ${Math.min(i + batchSize, files.length)}/${files.length} files`);
    }
    
    // Step 4: For significant issues, generate potential fixes
    const significantIssues = results.issues.filter(issue => issue.severity >= 7);
    if (significantIssues.length > 0) {
      logger.info(`Generating fixes for ${significantIssues.length} significant issues`);
      
      const fixResults = await debugOrchestrator.executeTask("FixGenerator", {
        issues: significantIssues
      });
      
      results.fixes = fixResults.fixes;
    }
    
    logger.info(`Debug scan complete. Found ${results.issues.length} issues, generated ${results.fixes.length} potential fixes`);
    return results;
  } catch (error) {
    logger.error(`Error in debug coordination: ${error.message}`);
    return {
      error: error.message,
      issues: results.issues,
      fixes: results.fixes
    };
  }
});

// Export both the class and the instance
module.exports = {
  AgentOrchestrator,
  debugOrchestrator
};
