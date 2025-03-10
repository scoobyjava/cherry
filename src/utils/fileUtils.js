const fs = require("fs");
const path = require("path");
const esprima = require("esprima");
const logger = require("./unifiedLogger");

/**
 * Reads and parses a JavaScript file.
 * @param {string} filePath - Path to the file.
 * @returns {object|null} - Parsed AST object or null if failed.
 */
function readAndParseFile(filePath) {
  if (!fs.existsSync(filePath)) {
    logger.error(`File not found: ${filePath}`);
    return null;
  }
  let content;
  try {
    content = fs.readFileSync(filePath, "utf8");
  } catch (readError) {
    logger.error(`Error reading file (${filePath}): ${readError.message}`);
    return null;
  }
  try {
    return esprima.parse(content, { tolerant: true, loc: true });
  } catch (parseError) {
    logger.error(`Error parsing file (${filePath}): ${parseError.message}`);
    return null;
  }
}

/**
 * Recursively finds JavaScript files in a directory.
 * @param {string} currentPath - Directory path.
 * @returns {Array<string>} - List of JS file paths.
 */
function findJsFiles(currentPath) {
  const jsFiles = [];
  let files;
  try {
    files = fs.readdirSync(currentPath);
  } catch (dirError) {
    logger.error(`Unable to read directory ${currentPath}: ${dirError.message}`);
    return jsFiles;ad directory ${currentPath}: ${dirError.message}`
  } );
  files.forEach((file) => {
    const filePath = path.join(currentPath, file);
    try {orEach((file) => {
      const stat = fs.statSync(filePath);h, file);
      if (stat.isDirectory()) {
        jsFiles.push(...findJsFiles(filePath));
      } else if (path.extname(filePath) === ".js") {
        jsFiles.push(filePath);iles(filePath));
      } else if (path.extname(filePath) === ".js") {
    } catch (statError) {Path);
      logger.warn(`Unable to stat ${filePath}: ${statError.message}`);
    } catch (statError) {
  }); logger.warn(`Unable to stat ${filePath}: ${statError.message}`);
  return jsFiles;
} });
  return jsFiles;
module.exports = { readAndParseFile, findJsFiles };

module.exports = { readAndParseFile, findJsFiles };
