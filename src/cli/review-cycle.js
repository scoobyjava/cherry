const { Command } = require('commander');
const path = require('path');
const fs = require('fs');
const ReviewCycle = require('../utils/reviewCycle');
const FeedbackDrivenDevelopment = require('../utils/feedbackIntegration');
const logger = require('../utils/unifiedLogger');

module.exports = {
  command: new Command('review')
    .description('Run an iterative review cycle on code')
    .argument('<file>', 'File to review')
    .option('-i, --iterations <number>', 'Maximum number of improvement iterations', 3)
    .option('-f, --feedback <file>', 'File containing user feedback')
    .option('-t, --tests <glob>', 'Test files to run against code')
    .action(async (file, options) => {
      try {
        // Read the file
        const filePath = path.resolve(process.cwd(), file);
        if (!fs.existsSync(filePath)) {
          logger.error(`File not found: ${filePath}`);
          process.exit(1);
        }
        
        const code = fs.readFileSync(filePath, 'utf8');
        logger.info(`Reviewing file: ${filePath}`, { codeLength: code.length });
        
        // Initialize systems
        const reviewCycle = new ReviewCycle();
        const feedbackSystem = new FeedbackDrivenDevelopment();
        
        // Process feedback if provided
        let result;
        if (options.feedback && fs.existsSync(options.feedback)) {
          const feedback = fs.readFileSync(options.feedback, 'utf8');
          result = await feedbackSystem.processUserFeedback(
            feedback, 
            { id: filePath, code }, 
            { filePath }
          );
        } else {
          // Run standard review
          result = await reviewCycle.runIterativeReview(
            code, 
            { filePath },
            options.iterations
          );
        }
        
        // Output results
        console.log('\n=== Review Results ===');
        console.log(`Iterations: ${result.iterations}`);
        console.log(`Quality Score: ${result.qualityScore}`);
        
        // Write improved code to file
        const outputPath = `${filePath}.improved`;
        fs.writeFileSync(outputPath, result.finalCode);
        console.log(`\nImproved code written to: ${outputPath}`);
        
        // Show summary of changes
        console.log('\n=== Summary of Improvements ===');
        result.reviews.forEach((review, i) => {
          console.log(`\nIteration ${i+1}:`);
          if (review.concerns) {
            const highCount = review.concerns.filter(c => c.severity === 'high').length;
            const medCount = review.concerns.filter(c => c.severity === 'medium').length;
            const lowCount = review.concerns.filter(c => c.severity === 'low').length;
            console.log(`Issues: ${highCount} high, ${medCount} medium, ${lowCount} low`);
          }
        });
      } catch (error) {
        logger.error('Review process failed:', error);
        process.exit(1);
      }
    }),
};
