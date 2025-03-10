const logger = require("../utils/unifiedLogger");
const { query, generateImage } = require("../integrations/huggingfaceClient");
const memorySystem = require("../memory/memorySystem");
const path = require("path");
const fs = require("fs").promises;
const axios = require('axios');
const HUGGINGFACE_API_TOKEN = process.env.HUGGINGFACE_API_TOKEN;
const MODEL = 'stabilityai/stable-diffusion-2';

async function generateLogo() {
  const prompt = "Create a logo for Cherry's Command Center that is modern, colorful, and friendly";
  const headers = {
    Authorization: `Bearer ${HUGGINGFACE_API_TOKEN}`,
    'Content-Type': 'application/json'
  };

  const payload = { inputs: prompt };
  try {
    const response = await axios.post(`https://api-inference.huggingface.co/models/${MODEL}`, payload, { headers });
    console.log('Generated Logo:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error generating logo:', error.toString());
    throw error;
  }
}

module.exports = { generateLogo };