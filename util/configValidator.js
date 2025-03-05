const { validateString, validateNumber, validateRequiredFields } = require('./validation');

/**
 * Validates the benchmark configuration
 * @param {Object} config - The configuration object to validate
 * @returns {Object} - Validation result with success flag and errors
 */
function validateBenchmarkConfig(config) {
  const errors = [];
  
  // Validate top level structure
  if (!validateRequiredFields(config, ['app'])) {
    errors.push('Missing required top-level "app" property');
    return { success: false, errors };
  }
  
  // Validate services
  if (!validateRequiredFields(config.app, ['services'])) {
    errors.push('Missing required "app.services" property');
  } else {
    const { services } = config.app;
    
    // Validate Pinecone service
    if (services.pinecone) {
      if (!validateString(services.pinecone.index_name, { minLength: 1 })) {
        errors.push('Invalid or missing pinecone.index_name');
      }
      
      if (services.pinecone.default_top_k !== undefined && 
          !validateNumber(services.pinecone.default_top_k, { min: 1, max: 1000, integer: true })) {
        errors.push('Invalid pinecone.default_top_k - must be an integer between 1 and 1000');
      }
      
      // Validate namespaces
      if (services.pinecone.namespaces) {
        Object.entries(services.pinecone.namespaces).forEach(([namespace, config]) => {
          if (!validateString(config.description, { minLength: 1 })) {
            errors.push(`Invalid or missing description for namespace: ${namespace}`);
          }
          
          if (config.default_top_k !== undefined && 
              !validateNumber(config.default_top_k, { min: 1, max: 1000, integer: true })) {
            errors.push(`Invalid default_top_k for namespace: ${namespace} - must be an integer between 1 and 1000`);
          }
          
          // Validate metadata schema
          if (config.metadata_schema) {
            if (typeof config.metadata_schema !== 'object') {
              errors.push(`Invalid metadata_schema for namespace: ${namespace} - must be an object`);
            }
          }
        });
      }
    }
    
    // Validate Postgres service
    if (services.postgres) {
      if (!validateString(services.postgres.database, { minLength: 1 })) {
        errors.push('Invalid or missing postgres.database');
      }
      
      if (services.postgres.query_settings && 
          !validateNumber(services.postgres.query_settings.statement_timeout_ms, 
            { min: 0, max: 300000, integer: true })) {
        errors.push('Invalid postgres.query_settings.statement_timeout_ms - must be an integer between 0 and 300000');
      }
    }
    
    // Validate OpenAI service
    if (services.openai) {
      if (services.openai.default_model !== undefined && 
          !validateString(services.openai.default_model, { minLength: 1 })) {
        errors.push('Invalid openai.default_model');
      }
      
      if (services.openai.max_tokens !== undefined && 
          !validateNumber(services.openai.max_tokens, { min: 1, max: 32768, integer: true })) {
        errors.push('Invalid openai.max_tokens - must be an integer between 1 and 32768');
      }
    }
  }
  
  // Validate port ranges
  if (config.app.validation?.port_ranges) {
    const { min, max } = config.app.validation.port_ranges;
    
    if (!validateNumber(min, { min: 0, max: 65535, integer: true })) {
      errors.push('Invalid port_ranges.min - must be an integer between 0 and 65535');
    }
    
    if (!validateNumber(max, { min: 1024, max: 65535, integer: true })) {
      errors.push('Invalid port_ranges.max - must be an integer between 1024 and 65535');
    }
    
    if (min >= max) {
      errors.push('Invalid port_ranges - min must be less than max');
    }
  }
  
  return {
    success: errors.length === 0,
    errors
  };
}

module.exports = {
  validateBenchmarkConfig
};
