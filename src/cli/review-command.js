const { Command } = require('commander');
const fs = require('fs');
const path = require('path');
const ReviewCycleManager = require('../utils/reviewCycleManager');
const logger = require('../utils/unifiedLogger');

module.exports = {
  command: new Command('review')
    .description('Run iterative code review and improvement cycle')
    .argument('<file>', 'File to review and improve')
    .option('-i, --iterations <number>', 'Maximum improvement iterations', '3')
    .option('-t, --threshold <number>', 'Quality threshold (0-100)', '85')
    .option('-f, --feedback <string>', 'File containing user feedback')
    .option('-e, --execute-tests', 'Run tests after improvements')
    .option('-o, --output <file>', 'Output file for improved code')
    .action(async (file, options) => {
      try {
        // Read target file
        const fullPath = path.resolve(process.cwd(), file);
        if (!fs.existsSync(fullPath)) {
          logger.error(`File not found: ${fullPath}`);
          process.exit(1);
        }
        
        const code = fs.readFileSync(fullPath, 'utf8');
        const fileId = path.basename(fullPath);
        
        // Initialize review cycle manager
        const reviewManager = new ReviewCycleManager({
          maxIterations: parseInt(options.iterations),
          qualityThreshold: parseInt(options.threshold)
        });
        
        // Add file metadata to context
        const context = {
          fileName: fileId,
          filePath: fullPath,
          fileType: path.extname(fullPath).substring(1),
          project: 'Cherry AI System'
        };
        
        // Run the review cycle
        console.log(`Starting iterative review cycle for ${fileId}...`);
        const result = await reviewManager.runIterativeReviewCycle(fileId, code, context);
        
        // Process user feedback if provided
        if (options.feedback && fs.existsSync(options.feedback)) {
          console.log(`Incorporating user feedback...`);
          const feedback = fs.readFileSync(options.feedback, 'utf8');
          const feedbackResult = await reviewManager.incorporateUserFeedback(
            fileId, 
            result.improvedCode, 
            feedback
          );
          result.improvedCode = feedbackResult.improvedCode;
          result.userFeedbackApplied = true;
