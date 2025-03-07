require("dotenv").config(); // Ensure environment variables are loaded

const { exec } = require("child_process");
const logger = require("../logger");
const fs = require("fs").promises;
const path = require("path");

// Memory store for service status history
const serviceMemory = {
  sonarqube: [],
  cody: [],
  summaries: [],
};

// Maximum entries to keep per service before summarizing
const MAX_MEMORY_ENTRIES = 50;

// Directory for storing persistent memory
const MEMORY_DIR = path.join(__dirname, "../../tmp/memory");
const MEMORY_FILE = path.join(MEMORY_DIR, "service-memory.json");

// Simple logger that censors sensitive keys
const SENSITIVE_KEYS = ["CHERRY_GH_TOKEN"];
function secureLog(level, message, data = {}) {
  // Remove sensitive keys from the data object before logging.
  const safeData = Object.keys(data).reduce((result, key) => {
    result[key] = SENSITIVE_KEYS.includes(key) ? "[REDACTED]" : data[key];
    return result;
  }, {});
  console[level](
    JSON.stringify({
      level,
      message,
      data: safeData,
      timestamp: new Date().toISOString(),
    })
  );
}

/**
 * Log a structured message (as JSON) for clarity in multi-agent communications.
 *
 * @param {string} level - Log level ("info", "error", etc.)
 * @param {string} message - Message to log
 * @param {object} [data={}] - Additional metadata
 */
function logStructured(level, message, data = {}) {
  const logEntry = {
    level,
    message,
    data,
    timestamp: new Date().toISOString(),
  };
  logger[level](JSON.stringify(logEntry));
}

/**
 * Store an event in the service memory
 * @param {string} service - Service name
 * @param {object} event - Event details
 */
async function recordServiceEvent(service, event) {
  if (!serviceMemory[service]) {
    serviceMemory[service] = [];
  }

  // Add event with timestamp
  const eventWithTimestamp = {
    ...event,
    timestamp: new Date().toISOString(),
  };

  serviceMemory[service].push(eventWithTimestamp);

  // Trigger summary if we have too many entries (Best Practice #1: Periodic Summaries)
  if (serviceMemory[service].length > MAX_MEMORY_ENTRIES) {
    await summarizeServiceHistory(service);
  }

  // Persist memory to disk
  await persistMemory();
}

/**
 * Summarize service history and compress the memory (Best Practice #1: Periodic Summaries)
 * @param {string} service - Service name
 */
async function summarizeServiceHistory(service) {
  if (!serviceMemory[service] || serviceMemory[service].length === 0) {
    return;
  }

  // Count status types
  const statusCounts = {
    running: 0,
    restarted: 0,
    failed: 0,
  };

  let firstTimestamp = serviceMemory[service][0].timestamp;
  let lastTimestamp =
    serviceMemory[service][serviceMemory[service].length - 1].timestamp;

  // Analyze events
  serviceMemory[service].forEach((event) => {
    if (event.status === "running") statusCounts.running++;
    if (event.status === "restarted") statusCounts.restarted++;
    if (event.status === "failed") statusCounts.failed++;
  });

  // Create summary
  const summary = {
    service,
    period: {
      start: firstTimestamp,
      end: lastTimestamp,
    },
    counts: statusCounts,
    uptime:
      ((statusCounts.running / serviceMemory[service].length) * 100).toFixed(
        2
      ) + "%",
    summary:
      `Service ${service} was running ${statusCounts.running} times, ` +
      `restarted ${statusCounts.restarted} times, and failed ${statusCounts.failed} times ` +
      `between ${new Date(firstTimestamp).toLocaleString()} and ${new Date(
        lastTimestamp
      ).toLocaleString()}.`,
  };

  // Store summary
  serviceMemory.summaries.push(summary);

  // Keep only recent events (pruning)
  serviceMemory[service] = serviceMemory[service].slice(-10);

  logStructured("info", `Memory summary generated for ${service}`, summary);
}

/**
 * Retrieve relevant service history based on query (Best Practice #2: Selective Historical Recall)
 * @param {string} service - Service name
 * @param {object} query - Query parameters
 * @returns {Array} - Relevant events
 */
function getRelevantServiceHistory(service, query = {}) {
  // Start with most recent events
  let relevantEvents = [...(serviceMemory[service] || [])];

  // Filter by status if specified in query
  if (query.status) {
    relevantEvents = relevantEvents.filter(
      (event) => event.status === query.status
    );
  }

  // Filter by time range if specified
  if (query.since) {
    const sinceTime = new Date(query.since).getTime();
    relevantEvents = relevantEvents.filter(
      (event) => new Date(event.timestamp).getTime() >= sinceTime
    );
  }

  // Find relevant summaries too
  const relevantSummaries = serviceMemory.summaries.filter(
    (summary) => summary.service === service
  );

  return {
    recentEvents: relevantEvents,
    historicalSummaries: relevantSummaries,
  };
}

/**
 * Persist memory to disk
 */
async function persistMemory() {
  try {
    await fs.mkdir(MEMORY_DIR, { recursive: true });
    await fs.writeFile(MEMORY_FILE, JSON.stringify(serviceMemory, null, 2));
  } catch (error) {
    logStructured("error", "Failed to persist memory", {
      error: error.message,
    });
  }
}

/**
 * Load memory from disk
 */
async function loadMemory() {
  try {
    const data = await fs.readFile(MEMORY_FILE, "utf8");
    const loadedMemory = JSON.parse(data);

    // Validate memory format before merging (Best Practice #3: Memory Validation)
    if (loadedMemory && typeof loadedMemory === "object") {
      Object.assign(serviceMemory, loadedMemory);
      logStructured("info", "Service memory loaded", {
        services: Object.keys(serviceMemory),
        summaryCount: serviceMemory.summaries?.length || 0,
      });
    }
  } catch (error) {
    // It's okay if the file doesn't exist yet
    if (error.code !== "ENOENT") {
      logStructured("warn", "Failed to load memory", { error: error.message });
    }
  }
}

/**
 * Check if a process is running.
 */
function checkProcess(processName, callback) {
  exec(`pgrep -f ${processName}`, (error, stdout, stderr) => {
    if (error || !stdout.trim()) {
      callback(false);
    } else {
      callback(true);
    }
  });
}

/**
 * Restart a process by running its start command.
 */
function restartProcess(processName, startCommand) {
  exec(startCommand, (error, stdout, stderr) => {
    if (error) {
      logStructured("error", `Failed to restart ${processName}`, {
        error: error.message,
      });

      // Record failure event
      recordServiceEvent(processName, {
        status: "failed",
        error: error.message,
      });
    } else {
      logStructured("info", `${processName} restarted successfully.`, {
        stdout: stdout.trim(),
      });

      // Record restart event
      recordServiceEvent(processName, {
        status: "restarted",
        stdout: stdout.trim(),
      });
    }
  });
}

/**
 * Auto-restart check for a given process.
 */
function autoRestart(processName, startCommand) {
  checkProcess(processName, (isRunning) => {
    if (!isRunning) {
      logStructured(
        "info",
        `${processName} not running. Attempting restart...`
      );
      restartProcess(processName, startCommand);
    } else {
      logStructured("info", `${processName} is running fine.`);

      // Record running event
      recordServiceEvent(processName, {
        status: "running",
      });
    }
  });
}

// Get commands from environment variables, if set
const SONARQUBE_CMD =
  process.env.SONARQUBE_START_CMD || "docker start sonarqube_container";
const CODY_CMD = process.env.CODY_START_CMD || "systemctl start cody-ai";

// Load memory on startup
loadMemory()
  .then(() => {
    // Scheduled checks for SonarQube and Cody every 60 seconds
    setInterval(() => {
      autoRestart("sonarqube", SONARQUBE_CMD);
      autoRestart("cody", CODY_CMD);
    }, 60000);

    // Run memory validation and cleanup every 24 hours
    setInterval(async () => {
      await validateMemoryIntegrity();
    }, 24 * 60 * 60 * 1000);
  })
  .catch((error) => {
    logStructured("error", "Failed to initialize service memory", {
      error: error.message,
    });
  });

/**
 * Validate memory integrity and prune redundant information (Best Practice #3: Memory Pruning)
 */
async function validateMemoryIntegrity() {
  // Check for duplicate summaries and remove them
  const uniqueSummaries = [];
  const summaryKeys = new Set();

  serviceMemory.summaries.forEach((summary) => {
    const key = `${summary.service}-${summary.period.start}-${summary.period.end}`;
    if (!summaryKeys.has(key)) {
      summaryKeys.add(key);
      uniqueSummaries.push(summary);
    }
  });

  // Remove duplicates
  if (uniqueSummaries.length !== serviceMemory.summaries.length) {
    logStructured("info", "Removed duplicate summaries", {
      before: serviceMemory.summaries.length,
      after: uniqueSummaries.length,
    });
    serviceMemory.summaries = uniqueSummaries;
  }

  // Persist cleaned memory
  await persistMemory();

  // Basic integrity test to ensure we haven't lost critical information
  for (const service of Object.keys(serviceMemory)) {
    if (service !== "summaries") {
      // Check if we have recent events for each service
      const hasRecentEvents = serviceMemory[service].some((event) => {
        const eventTime = new Date(event.timestamp).getTime();
        const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
        return eventTime > oneDayAgo;
      });

      if (!hasRecentEvents && serviceMemory[service].length > 0) {
        logStructured("warn", `No recent events found for ${service}`, {
          latestEvent:
            serviceMemory[service][serviceMemory[service].length - 1],
        });
      }
    }
  }

  return true;
}

module.exports = {
  autoRestart,
  getRelevantServiceHistory, // Export for external use
  summarizeServiceHistory, // Export for on-demand summaries
};

// GitHub Integration for CodeRabbit checks and other GitHub interactions
const CHERRY_GH_REPO =
  process.env.CHERRY_GH_REPO || "your_username/your_repo_name";
const CHERRY_GH_TOKEN =
  process.env.CHERRY_GH_TOKEN || "your_actual_github_personal_access_token";

// Optionally log the GitHub configuration (if safe)
logStructured("info", "GitHub integration configuration loaded", {
  CHERRY_GH_REPO,
});

// Simulated API function to fetch additional user info securely
async function fetchUserInfo(userId) {
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulated delay

  // Simulate failure for demonstration
  if (userId === 2) {
    throw new Error(`Failed to fetch info for user ${userId}`);
  }
  return { userId, info: `Additional info for user ${userId}` };
}

// Process an array of users asynchronously with full error handling
async function processUsers(users) {
  const results = [];
  const errors = [];

  const promises = users.map((user) =>
    fetchUserInfo(user.id)
      .then((info) => ({ status: "fulfilled", user, info }))
      .catch((error) => ({ status: "rejected", user, error }))
  );

  // Use Promise.allSettled to wait for all promises, even if some are rejected
  const outcomes = await Promise.allSettled(promises);
  outcomes.forEach((outcome) => {
    if (outcome.status === "fulfilled") {
      const { user, info } = outcome.value;
      results.push({ user, info });
    } else {
      // outcome.reason contains the error in rejected cases
      const { user, error } = outcome.reason || outcome.value;
      errors.push({ user, error: error ? error.message : "Unknown error" });
    }
  });

  secureLog("info", "Processed users", { results, errors });
  return { results, errors };
}

// Example user data (simulate your actual data source)
const users = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Charlie" },
];

processUsers(users)
  .then(({ results, errors }) => {
    if (errors.length === 0) {
      secureLog("info", "All users processed successfully");
    } else {
      secureLog("warn", "Some users encountered errors", { errors });
    }
  })
  .catch((error) => {
    secureLog("error", "Unexpected error during user processing", {
      error: error.message,
    });
  });

// GitHub integration (sensitive values are not logged publicly)
const CHERRY_GH_REPO =
  process.env.CHERRY_GH_REPO || "your_username/your_repo_name";
const CHERRY_GH_TOKEN = process.env.CHERRY_GH_TOKEN || "your_secret_token";

// When logging the GitHub configuration, omit or mask the token.
secureLog("info", "GitHub integration configuration loaded", {
  CHERRY_GH_REPO,
  CHERRY_GH_TOKEN, // This will be logged as [REDACTED]
});
