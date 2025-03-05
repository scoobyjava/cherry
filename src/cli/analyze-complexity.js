#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const esprima = require('esprima');
const cr = require('complexity-report');
const chalk = require('chalk');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse command line arguments
const argv = yargs(hideBin(process.argv))
  .option('file', {
    alias: 'f',
    description: 'File to analyze',
    type: 'string'
  })
  .option('directory', {
    alias: 'd',
    description: 'Directory to analyze recursively',
    type: 'string'
  })
  .help()
  .argv;

console.log(chalk.blue('Running code complexity analysis...'));

// Simple file analysis function
function analyzeFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      console.error(chalk.red(`File not found: ${filePath}`));
      return;
    }

    const code = fs.readFileSync(filePath, 'utf8');
    try {
      // Parse JavaScript using esprima
      const ast = esprima.parse(code, { loc: true });
      
      // Basic complexity calculation
      console.log(chalk.green(`Analysis for ${filePath}:`));
      console.log(`Lines of code: ${code.split('\n').length}`);
      console.log(`Functions: ${countFunctions(ast)}`);
    } catch (parseError) {
      console.error(chalk.yellow(`Error parsing ${filePath}: ${parseError.message}`));
    }
  } catch (error) {
    console.error(chalk.red(`Error analyzing ${filePath}: ${error.message}`));
  }
}

// Simple function to count functions in AST
function countFunctions(ast) {
  let count = 0;
  function traverse(node) {
    if (!node) return;
    
    if (node.type === 'FunctionDeclaration' || 
        node.type === 'FunctionExpression' ||
        node.type === 'ArrowFunctionExpression') {
      count++;
    }
    
    if (typeof node === 'object') {
      Object.keys(node).forEach(key => {
        if (key !== 'parent' && node[key] && typeof node[key] === 'object') {
          if (Array.isArray(node[key])) {
            node[key].forEach(item => traverse(item));
          } else {
            traverse(node[key]);
          }
        }
      });
    }
  }
  
  traverse(ast);
  return count;
}

// Check input arguments
if (argv.file) {
  analyzeFile(argv.file);
} else if (argv.directory) {
  console.log(chalk.yellow(`Directory analysis not implemented yet: ${argv.directory}`));
} else {
  console.log(chalk.yellow('Please provide either --file or --directory parameter'));
  console.log('Example: npm run analyze-complexity -- --file src/app.js');
}

main();
