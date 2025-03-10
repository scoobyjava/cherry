const { callLLM } = require('../utils/llmProvider');
const logger = require('../utils/unifiedLogger');

async function getCodeImprovementSuggestions(codeSnippet) {
  const prompt = `Suggest improvements for the following code in a concise bullet list:\n\n${codeSnippet}`;
  try {
    // You could allow switching providers by passing a second argument.
    const suggestions = await callLLM(prompt, 'openai');
    logger.info('Received code improvement suggestions', { suggestions });
    return suggestions;
  } catch (error) {
    logger.error('Error getting code improvement suggestions', { error: error.message });
    return null;
  }
}

module.exports = { getCodeImprovementSuggestions };
