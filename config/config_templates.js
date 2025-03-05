const fs = require('fs');
const path = require('path');

// Common configuration patterns
const commonPatterns = require('./common_patterns.json');

/**
 * Creates a connection config based on the provided type and custom settings
 * @param {string} type - 'basic' or 'extended'
 * @param {Object} customSettings - Override settings
 * @returns {Object} Connection configuration
 */
function createConnectionConfig(type = 'basic', customSettings = {}) {
  const baseConfig = type === 'extended' ? 
    commonPatterns.connection.extended : 
    commonPatterns.connection.basic;
  
  return {
    ...baseConfig,
    ...customSettings
  };
}

/**
 * Creates a backup configuration with standard settings and overrides
 * @param {Object} customSettings - Override settings
 * @param {string} schedule - Cron schedule expression
 * @param {string} location - Backup storage location
 * @returns {Object} Backup configuration
 */
function createBackupConfig(customSettings = {}, schedule = '0 2 * * *', location = '/secure/backups') {
  return {
    ...commonPatterns.backup.standard,
    schedule,
    location,
    ...customSettings
  };
}

/**
 * Generate namespace configuration with consistent settings
 * @param {string} description - Namespace description
 * @param {Object} metadataSchema - Schema definition
 * @param {Object} customSettings - Custom namespace settings
 * @returns {Object} Namespace configuration
 */
function createNamespaceConfig(description, metadataSchema, customSettings = {}) {
  return {
    description,
    metadata_schema: metadataSchema,
    ...commonPatterns.namespace.default,
    ...customSettings
  };
}

module.exports = {
  createConnectionConfig,
  createBackupConfig,
  createNamespaceConfig,
  commonPatterns
};
