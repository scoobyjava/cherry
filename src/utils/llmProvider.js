const axios = require('axios');
const logger = require('./unifiedLogger');

// Configuration for different providers can be set up in an external config file or via environment variables.
const providers = {
  openai: {
    apiKey: process.env.OPENAI_API_KEY,
    baseUrl: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
    model: process.env.OPENAI_MODEL || 'gpt-4'
  },
  venice: {
    apiKey: process.env.VENICE_API_KEY,
    baseUrl: process.env.VENICE_API_BASE_URL || 'https://api.venice.ai/v1',
    model: process.env.VENICE_MODEL || 'latest'
  }
};

function getProvider(providerName) {
  const provider = providers[providerName];
  if (!provider) {
    throw new Error(`Provider ${providerName} is not configured.`);
  }
  return provider;
}

/**
 * Unified function to call an LLM API.
 * @param {string} prompt The prompt to send.
 * @param {string} providerName The provider to use ('openai' or 'venice').
 * @returns {Promise<string>} The generated completion.
 */
async function callLLM(prompt, providerName = 'openai') {
  const provider = getProvider(providerName);
  try {
    if (providerName === 'openai') {
      const response = await axios.post(
        `${provider.baseUrl}/completions`,
        {
          model: provider.model,
          prompt,
          max_tokens: 150,
          temperature: 0.7
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${provider.apiKey}`
          }
        }
      );
      return response.data.choices[0].text.trim();
    } else if (providerName === 'venice') {
      const response = await axios.post(
        `${provider.baseUrl}/generate`,
        {
          model: provider.model,
          prompt,
          max_tokens: 150,
          temperature: 0.7
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${provider.apiKey}`
          }
        }
      );
      return response.data.result.trim();
    } else {
      throw new Error('Unsupported LLM provider');
    }
  } catch (error) {
    logger.error('LLM call failed', { error: error.message, provider: providerName });
    throw error;
  }
}

module.exports = {
  callLLM
};
