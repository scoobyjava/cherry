/**
 * Configuration validator for benchmark_config.json
 */

const fs = require('fs');
const path = require('path');
const cronParser = require('cron-parser');

/**
 * Validates benchmark configuration
 * @param {string} configPath - Path to configuration file
 * @returns {object} Validation result with errors and warnings
 */
function validateConfig(configPath) {
  const result = {
    valid: true,
    errors: [],
    warnings: []
  };

  try {
    // Read and parse configuration
    const rawConfig = fs.readFileSync(configPath, 'utf8');
    const config = JSON.parse(rawConfig);

    // Validate Pinecone configuration
    validatePineconeConfig(config.pinecone, result);
    
    // Validate Postgres configuration
    validatePostgresConfig(config.postgres, result);
    
    // Validate connection parameters
    validateConnectionParams(config, result);
    
    // Validate cron expressions
    validateCronExpressions(config, result);
    
    // Validate port numbers
    validatePortNumbers(config, result);
    
    // Validate secret references
    validateSecretReferences(config, result);

    // Summarize results
    result.valid = result.errors.length === 0;
    
  } catch (error) {
    result.valid = false;
    result.errors.push(`Failed to parse config: ${error.message}`);
  }

  return result;
}

function validatePineconeConfig(pinecone, result) {
  if (!pinecone) {
    result.errors.push('Missing Pinecone configuration');
    return;
  }
  
  // Check required fields
  if (!pinecone.api_key) {
    result.errors.push('Missing Pinecone API key');
  }
  
  if (!pinecone.environment) {
    result.errors.push('Missing Pinecone environment');
  }
  
  if (!pinecone.connection?.timeout_ms) {
    result.warnings.push('Pinecone connection timeout not specified');
  }
  
  // Validate namespaces
  if (!pinecone.namespaces || Object.keys(pinecone.namespaces).length === 0) {
    result.errors.push('No Pinecone namespaces defined');
  } else {
    for (const [name, namespace] of Object.entries(pinecone.namespaces)) {
      if (!namespace.vector_count_limit) {
        result.warnings.push(`Namespace ${name} has no vector count limit`);
      }
      if (!namespace.limit_handling) {
        result.warnings.push(`Namespace ${name} has no limit handling strategy`);
      }
    }
  }
}

function validatePostgresConfig(postgres, result) {
  if (!postgres) {
    result.errors.push('Missing Postgres configuration');
    return;
  }
  
  // Check required fields
  const requiredFields = ['host', 'port', 'database', 'user', 'password'];
  for (const field of requiredFields) {
    if (!postgres[field]) {
      result.errors.push(`Missing Postgres ${field}`);
    }
  }
  
  // Validate replication
  if (postgres.replication?.enabled) {
    if (!postgres.replication.monitoring) {
      result.warnings.push('Postgres replication enabled but monitoring not configured');
    }
  }
}

function validateConnectionParams(config, result) {
  // Check all services for connection parameters
  const services = ['pinecone', 'postgres', 'openai', 'google_cloud'];
  for (const service of services) {
    if (config[service] && !config[service].connection) {
      result.warnings.push(`${service} missing connection configuration`);
    }
  }
}

function validateCronExpressions(config, result) {
  // Validate backup schedules
  const validateCron = (cronExpr, context) => {
    try {
      cronParser.parseExpression(cronExpr);
    } catch (e) {
      result.errors.push(`Invalid cron expression in ${context}: ${cronExpr}`);
    }
  };
  
  if (config.pinecone?.backup?.schedule) {
    validateCron(config.pinecone.backup.schedule, 'Pinecone backup schedule');
  }
  
  if (config.postgres?.backup?.schedule) {
    validateCron(config.postgres.backup.schedule, 'Postgres backup schedule');
  }
}

function validatePortNumbers(config, result) {
  const validPortRange = (port) => port >= 1024 && port <= 65535;
  
  if (config.postgres?.port && !validPortRange(config.postgres.port)) {
    result.errors.push(`Invalid Postgres port: ${config.postgres.port}`);
  }
  
  // Check replica ports
  if (config.postgres?.replication?.replicas) {
    for (const [idx, replica] of config.postgres.replication.replicas.entries()) {
      if (replica.port && !validPortRange(replica.port)) {
        result.errors.push(`Invalid port for replica ${idx}: ${replica.port}`);
      }
    }
  }
}

function validateSecretReferences(config, result) {
  // Simple check for proper secret format
  const secretRegex = /\$\{([A-Z0-9_]+)\}/;
  const checkSecrets = (obj, path = '') => {
    if (!obj || typeof obj !== 'object') return;
    
    for (const [key, value] of Object.entries(obj)) {
      const currentPath = path ? `${path}.${key}` : key;
      
      if (typeof value === 'string' && value.startsWith('${') && !secretRegex.test(value)) {
        result.warnings.push(`Potentially invalid secret reference format at ${currentPath}: ${value}`);
      } else if (typeof value === 'object') {
        checkSecrets(value, currentPath);
      }
    }
  };
  
  checkSecrets(config);
}

module.exports = {
  validateConfig
};

// Run validation if called directly
if (require.main === module) {
  const configPath = process.argv[2] || path.join(__dirname, '../benchmark_config.json');
  const validationResult = validateConfig(configPath);
  
  console.log('Configuration validation results:');
  console.log(`Valid: ${validationResult.valid}`);
  
  if (validationResult.errors.length > 0) {
    console.log('\nErrors:');
    validationResult.errors.forEach(error => console.log(` - ${error}`));
  }
  
  if (validationResult.warnings.length > 0) {
    console.log('\nWarnings:');
    validationResult.warnings.forEach(warning => console.log(` - ${warning}`));
  }
  
  process.exit(validationResult.valid ? 0 : 1);
}
