// Main entry point for the Cherry website builder
const AgentRunner = require("./agents/agentRunner");
const logger = require("./logger");

async function main() {
  logger.info("Cherry website builder starting...");
  
  const cherry = new AgentRunner({ agentName: "cherry" });
  
  // Start periodic self-review of external tools if needed
  try {
    cherry.startSelfReviewInterval();
    logger.info("Cherry's self-review monitoring activated for external tools");
  } catch (err) {
    logger.warn(`Could not start tool monitoring: ${err.message}`);
  }
  
  const initialized = await cherry.init();
  if (!initialized) {
    logger.error("Failed to initialize Cherry agent runner");
    process.exit(1);
  }
  
  const buildResult = await cherry.startWebsiteBuild();
  
  if (buildResult.success) {
    logger.info("Website build process initiated successfully");
    logger.info("Check the task queue progress for updates");
  } else {
    logger.error(`Website build failed to start: ${buildResult.error}`);
  }
}

main().catch((err) => {
  logger.error(`Unhandled error in Cherry main process: ${err.message}`);
  process.exit(1);
});

<<<<<<< Tabnine <<<<<<<
async processTaskQueue() {
  const startTime = performance.now();//+
  // Process up to 5 tasks in parallel
  while (this.taskQueue.length > 0) {
    const tasksToProcess = this.taskQueue.splice(0, 5);
    await Promise.all(
      tasksToProcess.map(task => this.processTask(task))
    );

    // Log progress
    if (this.taskQueue.length > 0) {
      console.log(`Processed batch of ${tasksToProcess.length} tasks. ${this.taskQueue.length} remaining.`);
    }
  }
  console.log('All tasks completed.');
//+
  const endTime = performance.now();//+
  console.log(`Task queue processing completed in ${((endTime - startTime) / 1000).toFixed(2)} seconds`);//+
}
>>>>>>> Tabnine >>>>>>>// {"source":"chat"}
