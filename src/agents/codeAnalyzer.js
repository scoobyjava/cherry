const { exec } = require('child_process');
const { query } = require('../integrations/huggingfaceClient');
const logger = require('../utils/unifiedLogger');

function runCodeAnalysis() {
  // Run ESLint over the project and output JSON.
  exec('npx eslint . --format json', async (error, stdout, stderr) => {
    if (error) {
      logger.error(`Error running ESLint: ${error}`);
      return;
    }
    try {
      const analysisResults = JSON.parse(stdout);
      const issues = analysisResults.flatMap(file => 
        file.messages.map(msg => msg.message)
      ).join('. ');
      const prompt = { inputs: `Provide suggestions based on these code issues: ${issues}` };
      const suggestions = await query('sshleifer/distilbart-cnn-12-6', prompt);
      logger.info('Code Analysis Suggestions:', { suggestions });
    } catch (parseError) {
      logger.error('Error parsing ESLint output:', { error: parseError.toString() });
    }
  });
}

module.exports = { runCodeAnalysis };
