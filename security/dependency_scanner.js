const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const execPromise = util.promisify(exec);

/**
 * Scan npm dependencies for vulnerabilities
 * @param {string} projectPath - Path to the project root
 * @returns {Object} - Vulnerability report
 */
async function scanNpmDependencies(projectPath) {
  try {
    console.log(`Scanning npm dependencies in ${projectPath}...`);
    const { stdout } = await execPromise('npm audit --json', { cwd: projectPath });
    return JSON.parse(stdout);
  } catch (error) {
    // npm audit exits with non-zero code when vulnerabilities are found
    if (error.stdout) {
      return JSON.parse(error.stdout);
    }
    console.error('Error scanning npm dependencies:', error.message);
    return { error: error.message };
  }
}

/**
 * Scan Python dependencies for vulnerabilities
 * @param {string} requirementsPath - Path to requirements.txt
 * @returns {Object} - Vulnerability report
 */
async function scanPythonDependencies(requirementsPath) {
  try {
    console.log(`Scanning Python dependencies in ${requirementsPath}...`);
    // Using safety to check for vulnerabilities in Python dependencies
    const { stdout } = await execPromise(`safety check -r ${requirementsPath} --json`);
    return JSON.parse(stdout);
  } catch (error) {
    if (error.stdout) {
      return JSON.parse(error.stdout);
    }
    console.error('Error scanning Python dependencies:', error.message);
    return { error: error.message };
  }
}

/**
 * Find all package.json files in a directory recursively
 * @param {string} dir - Directory to start searching from
 * @returns {Array<string>} - Array of paths to package.json files
 */
function findPackageJsonFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  
  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory() && file !== 'node_modules' && !file.startsWith('.')) {
      results = results.concat(findPackageJsonFiles(filePath));
    } else if (file === 'package.json') {
      results.push(dir);
    }
  }
  
  return results;
}

/**
 * Find all requirements.txt files in a directory recursively
 * @param {string} dir - Directory to start searching from
 * @returns {Array<string>} - Array of paths to requirements.txt files
 */
function findRequirementsTxtFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  
  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory() && file !== 'venv' && !file.startsWith('.')) {
      results = results.concat(findRequirementsTxtFiles(filePath));
    } else if (file === 'requirements.txt') {
      results.push(filePath);
    }
  }
  
  return results;
}

module.exports = {
  scanNpmDependencies,
  scanPythonDependencies,
  findPackageJsonFiles,
  findRequirementsTxtFiles
};
