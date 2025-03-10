const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/unifiedLogger');

const FEEDBACK_LOG_PATH = path.join(__dirname, '../logs/feedback.log');

// Log developer feedback (e.g., on Cherry's recommendations)
// Expected feedbackData format: { features: [0.1, 0.2, 0.3], reward: 1.0 }
function logFeedback(feedbackData) {
  try {
    fs.appendFileSync(FEEDBACK_LOG_PATH, JSON.stringify(feedbackData) + "\n", 'utf8');
    logger.info("Feedback logged", { feedbackData });
  } catch (error) {
    logger.error("Error logging feedback", { error: error.toString() });
  }
}

// Trigger model training by executing a Python script.
function trainModel() {
  exec('python3 ml/learning_agent.py', (error, stdout, stderr) => {
    if (error) {
      logger.error('Error training model', { error: error.toString() });
      return;
    }
    logger.info('Training output', { stdout, stderr });
  });
}

module.exports = { logFeedback, trainModel };
