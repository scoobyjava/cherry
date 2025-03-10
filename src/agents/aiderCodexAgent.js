const logger = require("../utils/unifiedLogger");
const axios = require("axios");

/**
 * Calls the Aider-Codex API with the given parameters
 * @param {string} repo - The repository path
 * @param {string} token - Authentication token
 * @param {Object} params - Parameters for the Aider-Codex request
 * @returns {Promise<Object>} - The API response
 */
async function callAiderCodexAPI(repo, token, params) {
  try {
    const response = await axios.post(
      process.env.AIDER_CODEX_API_URL || "https://api.aider-codex.example.com/v1/process",
      {
        repository: repo,
        query: params.query || params.prompt,
        context: params.context,
        files: params.files || [],
        options: params.options || {}
      },
      {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      }
    );
    
    return response.data;
  } catch (error) {
    logger.error("Error calling Aider-Codex API", {
      error: error.message,
      statusCode: error.response?.status,
      responseData: error.response?.data
    });
    throw new Error(`Aider-Codex API error: ${error.message}`);
  }
}

async function aiderCodexHandler(params) {
  // Log the received parameters
  logger.info("aider-codex agent triggered", { params });

  // Validate required environment variables
  if (!process.env.CHERRY_CH_REPO) {
    throw new Error("CHERRY_CH_REPO environment variable is not set");
  }
  
  if (!process.env.CHERRY_CH_TOKEN) {
    throw new Error("CHERRY_CH_TOKEN environment variable is not set");
  }

  // Call the Aider-Codex API
  const response = await callAiderCodexAPI(
    process.env.CHERRY_CH_REPO,
    process.env.CHERRY_CH_TOKEN,
    params
  );
  
  // Process and return the response
  return {
    message: "aider-codex processing complete",
    result: response,
    changes: response.changes || [],
    suggestions: response.suggestions || []
  };
}

module.exports = {
  aiderCodexHandler,
  CHERRY_CH_REPO: 'your-org/your-repo',
  CHERRY_CH_TOKEN: 'your-auth-token',
  AIDER_CODEX_API_URL: 'https://api.aider-codex.example.com/v1/process'
};