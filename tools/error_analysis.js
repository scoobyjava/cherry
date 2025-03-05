#!/usr/bin/env node

/**
 * Error Handling Analysis Tool
 * 
 * This script analyzes the codebase to identify inconsistent error handling patterns.
 * It looks for:
 * - Missing try/catch blocks in async functions
 * - Inconsistent error logging
 * - Swallowed exceptions
 * - Inconsistent error types
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const config = {
  ignoreDirs: ['node_modules', '.git', 'dist', 'build'],
  fileExtensions: ['.js', '.ts', '.jsx', '.tsx'],
  errorPatterns: {
    swallowedErrors: /catch\s*\([^)]*\)\s*{(?!\s*(?:console|logger|throw|return))/g,
    inconsistentLogging: /console\.(log|warn|error)\s*\(\s*['"](error|err|exception)['"]/i,
    emptyBlocks: /catch\s*\([^)]*\)\s*{\s*}/g,
    errorConstructions: /new\s+Error\(/g
  }
};

// Find all relevant files
function findFiles(dir, extensions) {
  let results = [];
  const list = fs.readdirSync(dir);
  
  list.forEach(file => {
    file = path.join(dir, file);
    const stat = fs.statSync(file);
    
    if (stat.isDirectory() && !config.ignoreDirs.includes(path.basename(file))) {
      results = results.concat(findFiles(file, extensions));
    } else if (extensions.includes(path.extname(file))) {
      results.push(file);
    }
  });
  
  return results;
}

// Analyze a file for error handling patterns
function analyzeFile(filePath) {
  console.log(`Analyzing ${filePath}`);
  const content = fs.readFileSync(filePath, 'utf-8');
  const issues = [];
  
  // Check for swallowed exceptions
  const swallowedMatches = content.match(config.errorPatterns.swallowedErrors) || [];
  if (swallowedMatches.length > 0) {
    issues.push({
      type: 'swallowed_exception',
      count: swallowedMatches.length,
      severity: 'high'
    });
  }
  
  // Check for inconsistent logging
  const loggingMatches = content.match(config.errorPatterns.inconsistentLogging) || [];
  if (loggingMatches.length > 0) {
    issues.push({
      type: 'inconsistent_logging',
      count: loggingMatches.length,
      severity: 'medium'
    });
  }
  
  // Check for empty catch blocks
  const emptyBlockMatches = content.match(config.errorPatterns.emptyBlocks) || [];
  if (emptyBlockMatches.length > 0) {
    issues.push({
      type: 'empty_catch',
      count: emptyBlockMatches.length,
      severity: 'high'
    });
  }
  
  // Count error constructions
  const errorConstructions = content.match(config.errorPatterns.errorConstructions) || [];
  
  // Count try/catch blocks
  const tryBlocks = (content.match(/try\s*{/g) || []).length;
  const catchBlocks = (content.match(/catch\s*\(/g) || []).length;
  
  // Count async functions without try/catch
  const asyncFunctions = (content.match(/async\s+\w+\s*\([^)]*\)\s*{[^}]*}/g) || []);
  let asyncWithoutTry = 0;
  
  asyncFunctions.forEach(fn => {
    if (!fn.includes('try {')) {
      asyncWithoutTry++;
    }
  });
  
  if (asyncWithoutTry > 0) {
    issues.push({
      type: 'async_without_try',
      count: asyncWithoutTry,
      severity: 'medium'
    });
  }
  
  return {
    file: filePath,
    issues,
    stats: {
      tryBlocks,
      catchBlocks,
      errorConstructions: errorConstructions.length,
      asyncFunctions: asyncFunctions.length,
      asyncWithoutTry
    }
  };
}

// Main function
function main() {
  try {
    const rootDir = '/workspaces/cherry';
    const files = findFiles(rootDir, config.fileExtensions);
    
    const results = files.map(file => analyzeFile(file));
    
    // Generate report
    const summary = {
      totalFiles: results.length,
      filesWithIssues: results.filter(r => r.issues.length > 0).length,
      issuesByType: {},
      highSeverityIssues: 0,
      mediumSeverityIssues: 0,
      lowSeverityIssues: 0
    };
    
    results.forEach(result => {
      result.issues.forEach(issue => {
        if (!summary.issuesByType[issue.type]) {
          summary.issuesByType[issue.type] = 0;
        }
        summary.issuesByType[issue.type] += issue.count;
        
        if (issue.severity === 'high') {
          summary.highSeverityIssues += issue.count;
        } else if (issue.severity === 'medium') {
          summary.mediumSeverityIssues += issue.count;
        } else {
          summary.lowSeverityIssues += issue.count;
        }
      });
    });
    
    console.log('\n--- Error Handling Analysis Report ---');
    console.log(`Total files analyzed: ${summary.totalFiles}`);
    console.log(`Files with issues: ${summary.filesWithIssues}`);
    console.log('\nIssues by type:');
    Object.keys(summary.issuesByType).forEach(type => {
      console.log(`  - ${type}: ${summary.issuesByType[type]}`);
    });
    
    console.log('\nSeverity breakdown:');
    console.log(`  - High severity issues: ${summary.highSeverityIssues}`);
    console.log(`  - Medium severity issues: ${summary.mediumSeverityIssues}`);
    console.log(`  - Low severity issues: ${summary.lowSeverityIssues}`);
    
    // Output detailed results to file
    fs.writeFileSync(
      path.join(rootDir, 'error_handling_analysis.json'),
      JSON.stringify(results, null, 2)
    );
    
    console.log('\nDetailed results written to error_handling_analysis.json');
  } catch (error) {
    console.error('Error analyzing codebase:', error);
    process.exit(1);
  }
}

main();
