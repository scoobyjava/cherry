const logger = require("./unifiedLogger");

/**
 * AgentOrchestrator handles agent registration, caching, and task execution.
 */
class AgentOrchestrator {
  constructor() {
    this.agents = new Map();
    this.cache = new Map();
    this.activeTasks = new Set();
    this.pendingTasks = [];
    this.maxConcurrent = 4;
    this.cacheAge = 30 * 60 * 1000; // 30 minutes
  }

  registerAgent(name, handler, options = {}) {
    if (!name || typeof name !== "string") {
      throw new TypeError("Agent name must be a non-empty string");
    }
    if (typeof handler !== "function") {
      throw new TypeError("Agent handler must be a function");
    }
    if (this.agents.has(name)) {
      logger.warn(`Agent ${name} is being overwritten`);
    }
    const validatedOptions = {
      timeout: options.timeout || 60000,
      retries: options.retries || 0,
      ...options,
    };
    this.agents.set(name, {
      handler,
      options: validatedOptions,
      status: "idle",
      lastRun: null,
      successCount: 0,
      errorCount: 0,
      avgExecutionTime: 0,
    });
    logger.info(`Agent registered: ${name}`);
  }

  // Other methods (executeTask, getAgentStats, clearCache) remain similar with enhanced error handling...
}

module.exports = AgentOrchestrator;
