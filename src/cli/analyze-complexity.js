#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const esprima = require("esprima");
const chalk = require("chalk");
const yargs = require("yargs/yargs");
const { hideBin } = require("yargs/helpers");
const logger = require("../utils/unifiedLogger");
const { readAndParseFile, findJsFiles } = require("../utils/fileUtils");

// NEW: Default environment variable assignments to prevent duplicate declarations
if (!process.env.CHERRY_CH_REPO) {
  process.env.CHERRY_CH_REPO = "your-repo-name";
}
if (!process.env.CHERRY_CH_TOKEN) {
  process.env.CHERRY_CH_TOKEN = "your-token";
}

const getCurrentTime = () => {
  return (typeof performance !== 'undefined' && performance.now)
    ? performance.now()
    : Date.now();
};

const PerformanceTracker = {
  measurements: new Map(),
  start(label) {
    if (this.measurements.has(label)) {
      logger.warn(`Measurement with label ${label} already exists. Overwriting.`);
    }
    this.measurements.set(label, {
      startTime: getCurrentTime(),
      endTime: null,
      duration: null,
    });
  },
  end(label) {
    const measurement = this.measurements.get(label);
    if (!measurement) {
      logger.error(`No measurement found for label ${label}.`);
      return null;
    }
    measurement.endTime = getCurrentTime();
    measurement.duration = measurement.endTime - measurement.startTime;
    return measurement.duration;
  },
  summary() {
    return Array.from(this.measurements.entries())
      .filter(([_, m]) => m.duration !== null)
      .map(([label, m]) => ({
        operation: label,
        duration: `${m.duration.toFixed(2)}ms`,
      }));
  },
};

// High-performance agent orchestration
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
    // Input validation
    if (!name || typeof name !== 'string') {
      throw new TypeError('Agent name must be a non-empty string');
    }
    
    if (typeof handler !== 'function') {
      throw new TypeError('Agent handler must be a function');
    }
    
    // Check for duplicate agent
    if (this.agents.has(name)) {
      logger.warn(`Agent ${name} is being overwritten`);
    }
    
    // Validate options with defaults
    const validatedOptions = {
      timeout: options.timeout || 60000, // Default 60 second timeout
      retries: options.retries || 0,     // Default no retries
      ...options
    };
    
    // Register the agent with validated properties
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
async executeTask(agentName, params) {
  // Validate inputs
  if (!agentName) {
    logger.error('Missing required parameter: agentName');
    throw new Error('Agent name is required');
  }
  
  if (!this.agents.has(agentName)) {
    logger.error(`Unknown agent: ${agentName}`);
    throw new Error(`Agent not found: ${agentName}`);
  }
  
  // Safely create cache key with validation
  let cacheKey;
  try {
    cacheKey = `${agentName}:${JSON.stringify(params || {})}`;
  } catch (error) {
    logger.error(`Failed to serialize params for cache key: ${error.message}`);
    // Continue without caching
    cacheKey = null;
  }

  // Check cache if we have a valid cache key
  if (cacheKey && this.cache.has(cacheKey)) {
    try {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheAge) {
        logger.debug(`Cache hit for ${agentName}`, { params });
        return cached.result;
      }
      this.cache.delete(cacheKey); // Expired cache
    } catch (error) {
      logger.warn(`Cache access error: ${error.message}`);
      // Continue without caching
    }
  }

  // Queue task if at concurrency limit
  if (this.activeTasks.size >= this.maxConcurrent) {
    return new Promise((resolve, reject) => {
      this.pendingTasks.push({ agentName, params, resolve, reject });
      logger.debug(`Task queued: ${agentName} (queue length: ${this.pendingTasks.length})`);
    });
  }

  // Execute task with timeout protection
  try {
    return await Promise.race([
      this._executeTaskDirectly(agentName, params),
      new Promise((_, reject) => {
        setTimeout(() => reject(new Error(`Task execution timeout: ${agentName}`)), 
          this.agents.get(agentName)?.options?.timeout || 60000);
      })
    ]);
  } catch (error) {
    logger.error(`Task execution failed: ${agentName}`, { error: error.message });
    throw error; // Re-throw for caller to handle
  }
}
  async _executeTaskDirectly(agentName, params) {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Agent not found: ${agentName}`);
    }

    // Track active task
    const taskId = `${agentName}-${Date.now()}`;
    this.activeTasks.add(taskId);

    // Measure performance
    const startTime = performance.now();
    try {
      agent.status = "working";
      agent.lastRun = new Date();

      // Execute the agent
      const result = await agent.handler(params);

      // Cache the result
      const cacheKey = `${agentName}:${JSON.stringify(params)}`;
      this.cache.set(cacheKey, {
        result,
        timestamp: Date.now(),
      });

      // Update stats
      agent.successCount++;

      return result;
    } catch (error) {
      agent.errorCount++;
      logger.error(`Agent execution error: ${agentName}`, {
        error: error.message,
      });
      throw error;
    } finally {
      // Update execution time stats
      const executionTime = performance.now() - startTime;
      agent.avgExecutionTime =
        (agent.avgExecutionTime * (agent.successCount + agent.errorCount - 1) +
          executionTime) /
        (agent.successCount + agent.errorCount);

      // Clean up
      agent.status = "idle";
      this.activeTasks.delete(taskId);

      // Process next pending task if any
      if (this.pendingTasks.length > 0) {
        const nextTask = this.pendingTasks.shift();
        this._executeTaskDirectly(nextTask.agentName, nextTask.params)
          .then(nextTask.resolve)
          .catch(nextTask.reject);
      }
    }
  }

  getAgentStats() {
    try {
      return Array.from(this.agents.entries()).map(([name, agent]) => {
        // Use optional chaining and nullish coalescing for safety
        return {
          name,
          status: agent?.status || "unknown",
          successCount: agent?.successCount || 0,
          errorCount: agent?.errorCount || 0,
          avgExecutionTime: `${(agent?.avgExecutionTime || 0).toFixed(2)}ms`,
          lastRun: agent?.lastRun || null,
        };
      });
    } catch (error) {
      logger.error(`Failed to get agent stats: ${error.message}`);
      return []; // Return empty array rather than failing
    }
  }

  clearCache() {
    try {
      const size = this.cache.size;
      this.cache.clear();
      logger.info(`Agent cache cleared (${size} entries)`);
      return size;
    } catch (error) {
      logger.error(`Failed to clear cache: ${error.message}`);
      return 0;
    }
  }
}

// Agent real-time communication hub
class AgentCommunicationHub {
  constructor(server) {
    this.io = require('socket.io')(server);
    this.connections = new Map();
    this.messageHandlers = new Map();
    this.setupConnectionHandlers();
    // NEW: Fixed "routeInput" message handler registration
    this.registerMessageHandler("routeInput", async (data, caller, callback) => {
      try {
        const result = await routeUserRequest(data, agentName);
        callback({ success: true, result });
      } catch (error) {
        callback({ success: false, error: error.message });
      }
    });
  }

  setupConnectionHandlers() {
    this.io.on('connection', socket => {
      // Authenticate the connection
      socket.on('register', (data, callback) => {
        if (this.authenticateAgent(data)) {
          this.connections.set(data.agentId, {
            socket,
            info: {
              name: data.agentName,
              capabilities: data.capabilities,
              status: 'connected'
            }
          });
          logger.info(`Agent connected: ${data.agentName}`);
          callback({ success: true });
          // Notify others
          this.broadcast('agent:connected', {
            agentId: data.agentId,
            name: data.agentName
          });
        } else {
          callback({ success: false, error: 'Authentication failed' });
          socket.disconnect();
        }
      });

      // Handle agent messages
      socket.on('message', (message) => {
        this.handleAgentMessage(socket, message);
      });

      // Handle disconnection
      socket.on('disconnect', () => {
        let disconnectedAgentId = null;
        for (const [agentId, conn] of this.connections.entries()) {
          if (conn.socket === socket) {
            disconnectedAgentId = agentId;
            break;
          }
        }
        if (disconnectedAgentId) {
          const agentInfo = this.connections.get(disconnectedAgentId).info;
          logger.info(`Agent disconnected: ${agentInfo.name}`);
          this.connections.delete(disconnectedAgentId);
          // Notify others
          this.broadcast('agent:disconnected', {
            agentId: disconnectedAgentId,
            name: agentInfo.name
          });
        }
      });
    });
  }

  authenticateAgent(data) {
    // You would implement proper authentication here
    return data && data.agentId && data.agentName;
  }

  handleAgentMessage(socket, message) {
    if (!message || !message.type) return;
    // Find the sender
    let senderAgentId = null;
    for (const [agentId, conn] of this.connections.entries()) {
      if (conn.socket === socket) {
        senderAgentId = agentId;
        break;
      }
    }
    if (!senderAgentId) return;
    // Handle message
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(senderAgentId, message.data);
    }
    // Send to target agent if specified
    if (message.targetAgentId) {
      const targetConn = this.connections.get(message.targetAgentId);
      if (targetConn) {
        targetConn.socket.emit('message', {
          type: message.type,
          data: message.data,
          from: senderAgentId
        });
      }
    // Or broadcast if it's a broadcast message
    } else if (message.broadcast) {
      this.broadcast(message.type, message.data, senderAgentId);
    }
  }

  broadcast(type, data, excludeAgentId = null) {
    this.connections.forEach((conn, agentId) => {
      if (agentId !== excludeAgentId) {
        conn.socket.emit('message', { type, data });
      }
    });
  }

  registerMessageHandler(type, handler) {
    this.messageHandlers.set(type, handler);
    return this;
  }

  getConnectedAgents() {
    return Array.from(this.connections.entries())
      .map(([agentId, conn]) => ({
        id: agentId,
        ...conn.info
      }));
  }
}

// High-performance memory system
class MemorySystem {
  constructor(options = {}) {
    this.memory = {
      episodic: new Map(),
      semantic: new Map(),
      procedural: new Map(),
    };
    this.options = {
      persistPath: path.join(__dirname, "../data/memory"),
      persistInterval: 5 * 60 * 1000, // 5 minutes
      maxEntries: 1000,
      ...options,
    };
    // Ensure persistence directory exists
    if (!fs.existsSync(this.options.persistPath)) {
      fs.mkdirSync(this.options.persistPath, { recursive: true });
    }
    // Load persisted memory
    this._loadMemory();

    // Set up persistence interval
    if (this.options.persistInterval > 0) {
      this.persistTimer = setInterval(() => {
        this._persistMemory();
      }, this.options.persistInterval);
    }
  }

  store(type, key, data, metadata = {}) {
    if (!this.memory[type]) {
      throw new Error(`Invalid memory type: ${type}`);
    }
    const entry = {
      data,
      metadata: {
        created: Date.now(),
        accessed: Date.now(),
        accessCount: 0,
        ...metadata,
      },
    };
    this.memory[type].set(key, entry);
    // Prune if too many entries
    if (this.memory[type].size > this.options.maxEntries) {
      this._pruneMemory(type);
    }

    return key;
  }

  retrieve(type, key) {
    if (!this.memory[type]) {
      throw new Error(`Invalid memory type: ${type}`);
    }
    const entry = this.memory[type].get(key);
    if (!entry) return null;
    // Update access metadata
    entry.metadata.accessed = Date.now();
    entry.metadata.accessCount++;

    return entry.data;
  }

  search(type, query) {
    if (!this.memory[type]) {
      throw new Error(`Invalid memory type: ${type}`);
    }
    const results = [];
    this.memory[type].forEach((entry, key) => {
      let match = false;
      // Simple text search on stringified data
      const dataStr = JSON.stringify(entry.data).toLowerCase();
      if (dataStr.includes(query.toLowerCase())) {
        match = true;
      }
      // Check tags if they exist
      if (entry.metadata.tags && Array.isArray(entry.metadata.tags)) {
        if (
          entry.metadata.tags.some((tag) =>
            tag.toLowerCase().includes(query.toLowerCase())
          )
        ) {
          match = true;
        }
      }
      if (match) {
        results.push({ key, data: entry.data, metadata: entry.metadata });
      }
    });

    return results;
  }

  _pruneMemory(type) {
    // Sort by least recently accessed and remove oldest 20%
    const entries = Array.from(this.memory[type].entries());
    entries.sort((a, b) => a[1].metadata.accessed - b[1].metadata.accessed);
    const pruneCount = Math.floor(this.memory[type].size * 0.2);
    for (let i = 0; i < pruneCount; i++) {
      if (entries[i]) {
        this.memory[type].delete(entries[i][0]);
      }
    }

    logger.info(`Pruned ${pruneCount} entries from ${type} memory`);
  }

  _persistMemory() {
    Object.keys(this.memory).forEach((type) => {
      const filePath = path.join(this.options.persistPath, `${type}.json`);
      try {
        const data = JSON.stringify(Array.from(this.memory[type].entries()));
        fs.writeFileSync(filePath, data);
        logger.debug(
          `Persisted ${type} memory (${this.memory[type].size} entries)`
        );
      } catch (error) {
        logger.error(`Failed to persist ${type} memory: ${error.message}`);
      }
    });
  }

  _loadMemory() {
    Object.keys(this.memory).forEach((type) => {
      const filePath = path.join(this.options.persistPath, `${type}.json`);
      try {
        if (fs.existsSync(filePath)) {
          const data = fs.readFileSync(filePath, "utf8");
          const parsed = JSON.parse(data);
          this.memory[type] = new Map(parsed);
          logger.info(
            `Loaded ${type} memory (${this.memory[type].size} entries)`
          );
        }
      } catch (error) {
        logger.error(`Failed to load ${type} memory: ${error.message}`);
      }
    });
  }
}

// Parse command line arguments
const argv = yargs(hideBin(process.argv))
  .option("file", {
    describe: "Path to the file to analyze",
    type: "string",
  })
  .option("directory", {
    alias: "d",
    describe: "Directory to analyze recursively",
    type: "string",
  })
  .fail((msg, err, yargs) => {
    if (err) throw err; // preserve stack trace
    console.error("Error:", msg);
    console.error("Usage:", yargs.help());
    process.exit(1);
  })
  .argv;

/**
 * Calculates cyclomatic complexity by traversing the AST.
 * @param {object} ast - The AST object.
 * @returns {number} - Cyclomatic complexity.
 */
function calculateComplexity(ast) {
  let complexity = 1;
  function traverse(node) {
    if (!node || typeof node !== "object") return;
    switch (node.type) {
      case "IfStatement":
      case "ConditionalExpression":
      case "SwitchCase":
      case "ForStatement":
      case "WhileStatement":
      case "DoWhileStatement":
      case "CatchClause":
        complexity++;
        break;
      case "LogicalExpression":
        if (node.operator === "&&" || node.operator === "||") complexity++;
        break;
      default:
        break;
    }
    Object.keys(node).forEach((key) => {
      if (key !== "parent" && node[key] && typeof node[key] === "object") {
        if (Array.isArray(node[key])) {
          node[key].forEach(traverse);
        } else {
          traverse(node[key]);
        }
      }
    });
  }
  traverse(ast);
  return complexity;
}

/**
 * Processes a batch of files to analyze their complexity.
 * @param {Array<string>} fileBatch - Array of file paths.
 * @returns {Promise<Array<object>>} - Array of analysis results.
 */
async function processFileBatch(fileBatch) {
  const results = [];
  for (const file of fileBatch) {
    try {
      const ast = readAndParseFile(file);
      if (!ast) continue;
      const complexity = calculateComplexity(ast);
      const code = fs.readFileSync(file, "utf8");
      results.push({
        filePath: file,
        linesOfCode: code.split("\n").length,
        cyclomaticComplexity: complexity,
      });
    } catch (error) {
      logger.error(`Failed to analyze file: ${file}. Error: ${error.message}`);
      // Continue processing remaining files
    }
  }
  return results;
}

// Main execution logic (example)
async function main() {
  if (argv.file) {
    const result = await processFileBatch([argv.file]);
    console.log(result);
  } else if (argv.directory) {
    const jsFiles = findJsFiles(argv.directory);
    const result = await processFileBatch(jsFiles);
    console.log(result);
  } else {
    console.error("No file or directory provided.");
    process.exit(1);
  }
}

const AgentOrchestrator = require("../utils/agentOrchestrator");

if (typeof main === "function") {
  main();
}