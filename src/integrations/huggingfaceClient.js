const axios = require("axios");
const logger = require("../utils/unifiedLogger");

const API_URL = "https://api-inference.huggingface.co/models/";
const HUGGINGFACE_API_TOKEN = process.env.HUGGINGFACE_API_TOKEN;

// Cache for API responses
const cache = new Map();
const CACHE_TTL = 3600 * 1000; // 1 hour cache lifetime

/**
 * Query the Hugging Face Inference API
 * @param {string} model - The model identifier (e.g., 'gpt2')
 * @param {Object} options - Request options
 * @param {string} options.inputs - Input text for the model
 * @param {Object} [options.parameters] - Model-specific parameters
 * @param {boolean} [skipCache=false] - Whether to skip cache lookup
 * @returns {Promise<any>} - The model's response
 */
async function query(model, options, skipCache = false) {
  // Generate cache key based on model and options
  const cacheKey = `${model}:${JSON.stringify(options)}`;

  // Check cache first if not skipping
  if (!skipCache && cache.has(cacheKey)) {
    const cachedResult = cache.get(cacheKey);
    if (Date.now() - cachedResult.timestamp < CACHE_TTL) {
      logger.debug("Using cached Hugging Face response", { model });
      return cachedResult.data;
    } else {
      // Expired cache
      cache.delete(cacheKey);
    }
  }

  try {
    logger.debug("Querying Hugging Face model", { model, options });

    const headers = {
      Authorization: `Bearer ${HUGGINGFACE_API_TOKEN}`,
      "Content-Type": "application/json",
    };

    const response = await axios.post(`${API_URL}${model}`, options, { headers });

    // Cache the successful response
    cache.set(cacheKey, {
      data: response.data,
      timestamp: Date.now(),
    });

    return response.data;
  } catch (error) {
    // Check for model loading status
    if (error.response && error.response.status === 503) {
      logger.info("Model is loading, retrying...", { model });

      // Wait for the model to load
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Retry the request (recursive call, but should only happen once or twice)
      return query(model, options, skipCache);
    }

    logger.error("Error querying Hugging Face model", {
      model,
      error: error.message,
      status: error.response?.status,
    });

    throw new Error(`Hugging Face API error: ${error.message}`);
  }
}

/**
 * Get embeddings for a text using a Hugging Face model
 * @param {string} text - Text to embed
 * @param {string} [model='sentence-transformers/all-MiniLM-L6-v2'] - Embedding model
 * @returns {Promise<number[]>} - Vector embedding
 */
async function getEmbedding(
  text,
  model = "sentence-transformers/all-MiniLM-L6-v2"
) {
  try {
    const response = await query(model, {
      inputs: text,
    });

    // The response format depends on the model
    // For sentence-transformers, it's typically a flat array
    return response;
  } catch (error) {
    logger.error("Error getting embedding", { error: error.message });
    throw error;
  }
}

/**
 * Generate an image based on a text description
 * @param {string} prompt - Text description of the image
 * @param {Object} [options] - Generation options
 * @returns {Promise<string>} - Base64 encoded image
 */
async function generateImage(prompt, options = {}) {
  try {
    const model = options.model || "stabilityai/stable-diffusion-2-1";

    const response = await query(model, {
      inputs: prompt,
      parameters: {
        negative_prompt: options.negative_prompt || "",
        num_inference_steps: options.steps || 30,
        guidance_scale: options.guidance_scale || 7.5,
        ...options.parameters,
      },
    });

    return response; // This is typically a base64 encoded image
  } catch (error) {
    logger.error("Error generating image", { error: error.message });
    throw error;
  }
}

module.exports = {
  query,
  getEmbedding,
  generateImage,
};