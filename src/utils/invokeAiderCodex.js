const agents = require("../config/agents");
const logger = require("./unifiedLogger");

/**
 * Invokes the Aider-Codex agent with the specified parameters
 * @param {Object} params - Parameters for the Aider-Codex agent
 * @returns {Promise<Object>} - The result from the Aider-Codex agent
 */
async function invokeAiderCodex(params) {
  try {
    logger.info("Invoking Aider-Codex agent", { params });
    const result = await agents["aider-codex"].handler(params);
    return result;
  } catch (error) {
    logger.error("Error invoking Aider-Codex agent", { error: error.message });
    throw error;
  }
}

module.exports = invokeAiderCodex;
