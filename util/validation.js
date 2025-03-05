/**
 * Validation utilities for configuration and input parameters
 */

/**
 * Validate a string value against constraints
 * @param {string} value - The string to validate
 * @param {Object} options - Validation options
 * @param {number} [options.minLength] - Minimum length
 * @param {number} [options.maxLength] - Maximum length
 * @param {RegExp} [options.pattern] - Regex pattern to match
 * @returns {boolean} - Whether the string is valid
 */
function validateString(value, options = {}) {
  if (typeof value !== 'string') return false;
  
  if (options.minLength !== undefined && value.length < options.minLength) return false;
  if (options.maxLength !== undefined && value.length > options.maxLength) return false;
  if (options.pattern !== undefined && !options.pattern.test(value)) return false;
  
  return true;
}

/**
 * Validate a number value against constraints
 * @param {number} value - The number to validate
 * @param {Object} options - Validation options
 * @param {number} [options.min] - Minimum value
 * @param {number} [options.max] - Maximum value
 * @param {boolean} [options.integer] - Whether the number must be an integer
 * @returns {boolean} - Whether the number is valid
 */
function validateNumber(value, options = {}) {
  if (typeof value !== 'number' || isNaN(value)) return false;
  
  if (options.min !== undefined && value < options.min) return false;
  if (options.max !== undefined && value > options.max) return false;
  if (options.integer === true && !Number.isInteger(value)) return false;
  
  return true;
}

/**
 * Validate port number
 * @param {number} port - The port number to validate
 * @param {Object} config - The configuration object
 * @returns {boolean} - Whether the port number is valid
 */
function validatePort(port, config) {
  const minPort = config?.app?.validation?.port_ranges?.min || 1024;
  const maxPort = config?.app?.validation?.port_ranges?.max || 65535;
  
  return validateNumber(port, {
    min: minPort,
    max: maxPort,
    integer: true
  });
}

/**
 * Validate an object has all required fields
 * @param {Object} obj - The object to validate
 * @param {string[]} requiredFields - List of required field names
 * @returns {boolean} - Whether the object is valid
 */
function validateRequiredFields(obj, requiredFields) {
  if (!obj || typeof obj !== 'object') return false;
  
  return requiredFields.every(field => obj[field] !== undefined);
}

module.exports = {
  validateString,
  validateNumber,
  validatePort,
  validateRequiredFields
};
