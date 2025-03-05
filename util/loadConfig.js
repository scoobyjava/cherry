const fs = require('fs');
const path = require('path');
const { validateBenchmarkConfig } = require('./configValidator');

/**
 * Loads and validates a configuration file
 * @param {string} configPath - Path to the configuration file
 * @returns {Object} - The loaded and validated configuration
 * @throws {Error} - If the configuration is invalid or the file cannot be loaded
 */
function loadConfig(configPath) {
  try {
    // Check if file exists
    if (!fs.existsSync(configPath)) {
      throw new Error(`Configuration file not found: ${configPath}`);
    }
    
    // Read and parse the configuration file
    const configContent = fs.readFileSync(configPath, 'utf8');
    let config;
    
    try {
      config = JSON.parse(configContent);
    } catch (err) {
      throw new Error(`Invalid JSON in configuration file: ${err.message}`);
    }
    
    // Process environment variables in the configuration
    config = processEnvVars(config);
    
    // Validate the configuration
    const validation = validateBenchmarkConfig(config);
    if (!validation.success) {
      throw new Error(`Invalid configuration: ${validation.errors.join(', ')}`);
    }
    
    return config;
  } catch (err) {
    console.error(`Error loading configuration: ${err.message}`);
    throw err;
  }
}

/**
 * Processes environment variables in the configuration
 * @param {Object} config - The configuration object
 * @returns {Object} - The processed configuration
 */
function processEnvVars(config) {
  const configStr = JSON.stringify(config);
  
  // Replace environment variable placeholders with their values
  const processedStr = configStr.replace(/\${([^}]+)}/g, (match, envVar) => {
    const value = process.env[envVar];
    if (value === undefined) {
      console.warn(`Environment variable not found: ${envVar}`);
      return match; // Keep the placeholder if the environment variable is not defined
    }
    return value;
  });
  
  return JSON.parse(processedStr);
}

module.exports = {
  loadConfig
};
