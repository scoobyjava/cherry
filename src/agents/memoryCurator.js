const cron = require('node-cron');
const { query } = require('../integrations/huggingfaceClient');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/unifiedLogger');

const MEMORY_LOG_PATH = path.join(__dirname, '../logs/cherryMemory.log');

async function summarizeMemory() {
  try {
    const memoryText = fs.readFileSync(MEMORY_LOG_PATH, 'utf8');
    const prompt = { inputs: memoryText };
    // Use a summarization model such as "sshleifer/distilbart-cnn-12-6".
    const summary = await query('sshleifer/distilbart-cnn-12-6', prompt);
    logger.info('Daily Memory Summary:', { summary });
    fs.writeFileSync(path.join(__dirname, '../logs/memorySummary.log'), JSON.stringify(summary), 'utf8');
  } catch (error) {
    logger.error('Error summarizing memory:', { error: error.toString() });
  }
}

// Schedule to run daily at 8 AM.
cron.schedule('0 8 * * *', () => {
  logger.info("Running daily Memory Curator job...");
  summarizeMemory();
});

module.exports = { summarizeMemory };