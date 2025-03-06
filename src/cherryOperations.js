const logger = require("./logger");

/**
 * Makes a simulated API call with retry logic.
 * Retries up to 3 times before throwing an error.
 */
async function performApiCall() {
  let attempts = 0;
  const maxAttempts = 3;
  while (attempts < maxAttempts) {
    try {
      attempts++;
      // Replace simulateApiCall() with your actual API call logic.
      const response = await simulateApiCall();
      return { status: "success", data: response };
    } catch (err) {
      logger.error(`API call attempt ${attempts} failed: ${err.message}`);
      if (attempts < maxAttempts) {
        logger.info("Retrying API call");
      } else {
        throw err;
      }
    }
  }
}

/**
 * Updates the database. On failure, logs the error and retries once.
 */
async function updateDatabase() {
  try {
    // Replace simulateDbUpdate() with your actual DB update logic.
    return await simulateDbUpdate();
  } catch (err) {
    logger.error(`DB update failed: ${err.message}`);
    logger.info("Retrying DB update");
    return await simulateDbUpdate();
  }
}

/**
 * Delegates an agent task. If the primary agent fails, falls back to an alternative.
 */
async function delegateAgentTask() {
  try {
    // Attempt to delegate to the primary agent.
    return await simulateDelegateTask("primary");
  } catch (err) {
    logger.error(`Primary agent failure: ${err.message}`);
    logger.info("Fallback to alternative agent");
    return await simulateDelegateTask("alternative");
  }
}

/* --- Pseudo-Implementations for Simulation --- */
/* In real code, replace these simulated functions with actual logic. */
async function simulateApiCall() {
  // This function can be overridden in tests via spies.
  return "Simulated API Data";
}

async function simulateDbUpdate() {
  return { status: "success" };
}

async function simulateDelegateTask(agent) {
  if (agent === "primary") {
    // In tests, this function is overridden to simulate failure.
    return { status: "success", delegatedTo: "primary agent" };
  } else {
    return { status: "success", delegatedTo: "alternative agent" };
  }
}

module.exports = {
  performApiCall,
  updateDatabase,
  delegateAgentTask,
};
