<<<<<<< Tabnine <<<<<<<
const { exec } = require("child_process");//-
const logger = require("../logger");
const path = require("path");//-
const fs = require("fs").promises;//-
const crypto = require("crypto");//-

// Use dynamic import for fetch//-
const fetch = (...args) =>//-
  import("node-fetch").then(({ default: fetch }) => fetch(...args));//-
//-
/**//-
 * AgentRunner class for managing Cherry's agent operations//-
 * and website building process//-
 *///-
class AgentRunner {
  constructor(options = {}) {//-
    this.agentName = options.agentName || "cherry";//-
  constructor({ agentName }) {//+
    this.agentName = agentName;//+
    this.taskQueue = [];
    this.isProcessing = false;//-
    this.knowledge_base = {//-
      integrate: (data) => {//-
        // Simple implementation of knowledge base integration//-
        logger.info(`[${this.agentName}] Adding to knowledge base: ${data.type}`);//-
        // In a real implementation, you would store this data somewhere//-
      }//-
    };//-
    this.decisionHistory = [];//-
    this.availableTools = {//-
      n8n: false,//-
      sonarqube: false,//-
      cody: false,//-
      coderabbit: false//-
    };//-
//-
    // Security patterns to check in code//-
    this.sensitivePatterns = [//-
      /(['"](api[_-]?key|api[_-]?secret|password|secret|token|key)['"]\s*[:=]\s*['"])[^'"]+(['"])/gi,//-
      /(['"](ACCESS[_-]?KEY|SECRET[_-]?KEY)['"]\s*[:=]\s*['"])[^'"]+(['"])/gi,//-
      /(['"](GITHUB[_-]?TOKEN)['"]\s*[:=]\s*['"])[^'"]+(['"])/gi,//-
      /(const|let|var)\s+\w+\s*=\s*process\.env\.\w+/gi,//-
      /(['"](aws|gcp|azure)[_-]?(secret|token|key)['"]\s*[:=]\s*['"])[^'"]+(['"])/gi//-
    ];//-
  }

  async init() {
    try {//-
      logger.info(`${this.agentName} agent runner initializing...`);//-
//-
      // Create necessary directories if they don't exist//-
      await this.createDirectories();//-
//-
      // Check if needed agents exist, if not create them//-
      await this.ensureAgentsExist();//-
//-
      logger.info(`${this.agentName} initialized project structure`);//-
      return true;//-
    } catch (err) {//-
      logger.error(`Initialization error: ${err.message}`);//-
      return false;//-
    }//-
    // Initialize agent-specific resources//+
    logger.info(`Initializing ${this.agentName} agent`);//+
    // Add initialization logic here//+
    return true;//+
  }

  async createDirectories() {//-
    const dirs = [//-
      'src/components',//-
      'src/containers',//-
      'src/hooks',//-
      'src/styles',//-
      'src/utils',//-
      'tmp'//-
    ];//-
//-
    for (const dir of dirs) {//-
      try {//-
        await fs.mkdir(path.join(process.cwd(), dir), { recursive: true });//-
      } catch (err) {//-
        if (err.code !== 'EEXIST') {//-
          throw err;//-
        }//-
      }//-
    }//-
  startSelfReviewInterval() {//+
    // Implement periodic self-review logic//+
    setInterval(() => {//+
      logger.info(`${this.agentName} agent performing self-review`);//+
      // Add self-review logic here//+
    }, 3600000); // Run every hour//+
  }

  async ensureAgentsExist() {//-
    // Check if Python agent files exist//-
    const agentFiles = [//-
      'src/agents/developer.py',//-
      'src/agents/code_agent.py',//-
      'src/agents/code_generator.py'//-
    ];//-
//-
    for (const file of agentFiles) {//-
      try {//-
        await fs.access(path.join(process.cwd(), file));//-
      } catch (err) {//-
        if (err.code === 'ENOENT') {//-
          logger.warn(`Agent file ${file} doesn't exist`);//-
          // Would create placeholder files here in production//-
        }//-
      }//-
    }//-
  async startWebsiteBuild() {//+
    logger.info(`${this.agentName} agent starting website build`);//+
    // Add website build logic here//+
    return { success: true };//+
  }

  /**//-
   * Run a Python agent with the specified method and arguments//-
   * @param {string} agentName - Name of the agent (file without .py extension)//-
   * @param {string} method - Method to call within the agent//-
   * @param {object} args - Arguments to pass to the method//-
   * @returns {Promise<object>} - Result from the agent//-
   *///-
  async runPythonAgent(agentName, method, args = {}) {//-
    return new Promise((resolve, reject) => {//-
      const pythonScript = path.join(process.cwd(), 'src', 'agents', `${agentName}.py`);//-
//-
      // Create temporary directory if it doesn't exist//-
      const tmpDir = path.join(process.cwd(), 'tmp');//-
      fs.mkdir(tmpDir, { recursive: true })//-
        .then(() => {//-
          const tmpArgsFile = path.join(tmpDir, `${agentName}_args_${Date.now()}.json`);//-
          const tmpOutputFile = path.join(tmpDir, `${agentName}_output_${Date.now()}.json`);//-
//-
          return fs.writeFile(tmpArgsFile, JSON.stringify(args))//-
            .then(() => {//-
              logger.info(`Executing Python agent: ${agentName}.${method}`);//-
              // Execute the Python script with explicit python3 command//-
              const cmd = `python3 ${pythonScript} --method ${method} --args ${tmpArgsFile} --output ${tmpOutputFile}`;//-
//-
              exec(cmd, async (error, stdout, stderr) => {//-
                try {//-
                  if (error) {//-
                    logger.error(`Error running Python agent ${agentName}.${method}: ${error.message}`);//-
                    logger.error(`Python stdout: ${stdout}`);//-
                    logger.error(`Python stderr: ${stderr}`);//-
                    reject(error);//-
                    return;//-
                  }//-
//-
                  // Check if the output file exists//-
                  try {//-
                    await fs.access(tmpOutputFile);//-
                  } catch (err) {//-
                    logger.error(`Python agent output file not found: ${tmpOutputFile}`);//-
                    reject(new Error(`Python agent didn't create output file`));//-
                    return;//-
                  }//-
//-
                  // Read the output file//-
                  try {//-
                    const outputData = await fs.readFile(tmpOutputFile, 'utf8');//-
                    logger.info(`Python agent ${agentName}.${method} result received`);//-
//-
                    // Try to parse the JSON//-
                    try {//-
                      const result = JSON.parse(outputData);//-
//-
                      // Clean up temp files//-
                      await fs.unlink(tmpArgsFile).catch(() => {});//-
                      await fs.unlink(tmpOutputFile).catch(() => {});//-
//-
                      resolve(result);//-
                    } catch (jsonError) {//-
                      logger.error(`Error parsing Python agent output: ${jsonError.message}`);//-
                      logger.error(`Raw output: ${outputData.substring(0, 200)}...`); // Truncate for security//-
                      reject(jsonError);//-
                    }//-
                  } catch (readError) {//-
                    logger.error(`Error reading Python agent output: ${readError.message}`);//-
                    reject(readError);//-
                  }//-
                } catch (err) {//-
                  logger.error(`Unexpected error in Python agent execution: ${err.message}`);//-
                  reject(err);//-
                }//-
              });//-
            });//-
        })//-
        .catch(err => {//-
          logger.error(`Failed to prepare for Python agent: ${err.message}`);//-
          reject(err);//-
        });//-
    });//-
  }//-
//-
  /**//-
   * Queue a task for execution//-
   * @param {object} task - Task object with type, description, and data//-
   * @returns {object} - Success status and task ID//-
   *///-
  async queueTask(task) {//-
    this.taskQueue.push(task);//-
    logger.info(`Task queued: ${task.type} - ${task.description}`);//-
//-
    // Start processing if not already running//-
    if (!this.isProcessing) {//-
      this.processTaskQueue();//-
    }//-
//-
    return { success: true, taskId: this.taskQueue.length - 1 };//-
  }//-
//-
  /**//-
   * Process tasks in the queue//-
   *///-
  async processTaskQueue() {
    if (this.isProcessing || this.taskQueue.length === 0) {//-
      return;//-
    }//-
    const startTime = performance.now();//+
    while (this.taskQueue.length > 0) {//+
      const tasksToProcess = this.taskQueue.splice(0, 5);//+
      await Promise.all(//+
        tasksToProcess.map(task => this.processTask(task))//+
      );//+

    this.isProcessing = true;//-
//-
    const task = this.taskQueue.shift();//-
    logger.info(`Processing task: ${task.type} - ${task.description}`);//-
//-
    try {//-
      let result;//-
//-
      switch (task.type) {//-
        case 'generate-components'://-
          result = await this.generateComponents(task.data);//-
          break;//-
//-
        case 'write-file'://-
          // Security check before writing file//-
          if (this.isSafeToWrite(task.data.filePath, task.data.content)) {//-
            result = await this.writeFile(task.data.filePath, task.data.content);//-
          } else {//-
            throw new Error("Security check failed: Potentially unsafe content detected");//-
          }//-
          break;//-
//-
        case 'analyze-code-quality'://-
          result = await this.analyzeCodeQuality(task.data.target);//-
          break;//-
//-
        default://-
          logger.warn(`Unknown task type: ${task.type}`);//-
          result = { success: false, error: 'Unknown task type' };//-
      }//-
//-
      logger.info(`Task completed: ${task.type} - ${result.success ? 'Success' : 'Failed'}`);//-
    } catch (err) {//-
      logger.error(`Error processing task ${task.type}: ${err.message}`);//-
    } finally {//-
      this.isProcessing = false;//-
//-
      // Process next task if available//-
      if (this.taskQueue.length > 0) {
        setTimeout(() => this.processTaskQueue(), 100);//-
        logger.info(`Processed batch of ${tasksToProcess.length} tasks. ${this.taskQueue.length} remaining.`);//+
      }
    }
  }//-
    logger.info('All tasks completed.');//+

  /**//-
   * Check if content is safe to write (no sensitive information)//-
   * @param {string} filePath - Path where the file will be written//-
   * @param {string} content - Content to check//-
   * @returns {boolean} - True if safe, false otherwise//-
   *///-
  isSafeToWrite(filePath, content) {//-
    // Don't allow writing directly to sensitive directories//-
    const sensitiveDirectories = ['/etc', '/root', '/.ssh', '/.aws', '/.config'];//-
    if (sensitiveDirectories.some(dir => filePath.includes(dir))) {//-
      logger.error(`Security alert: Attempted to write to sensitive directory: ${filePath}`);//-
      return false;//-
    }//-
//-
    // Check for potential sensitive information in code//-
    for (const pattern of this.sensitivePatterns) {//-
      if (pattern.test(content)) {//-
        logger.error(`Security alert: Possible sensitive data detected in content for ${filePath}`);//-
        // Reset regex lastIndex after use//-
        pattern.lastIndex = 0;//-
//-
        // Sanitized content (redacting sensitive parts) could be stored for review//-
        const sanitized = content.replace(pattern, '$1[REDACTED]$3');//-
//-
        // Generate hash of the violation for security auditing//-
        const hash = crypto.createHash('sha256').update(sanitized).digest('hex').substring(0, 8);//-
        logger.error(`Security violation hash: ${hash}`);//-
//-
        return false;//-
      }//-
      // Reset regex lastIndex in case it was used before//-
      pattern.lastIndex = 0;//-
    }//-
//-
    return true;//-
    const endTime = performance.now();//+
    logger.info(`Task queue processing completed in ${((endTime - startTime) / 1000).toFixed(2)} seconds`);//+
  }

  /**//-
   * Generate website components//-
   * @param {object} data - Component generation data//-
   * @returns {object} - Success status//-
   *///-
  async generateComponents(data) {//-
    try {//-
      const result = await this.runPythonAgent('code_generator', 'generate_from_architecture');//-
//-
      if (result && result.success && result.tasks) {//-
        // Queue up the resulting tasks//-
        for (const task of result.tasks) {//-
          await this.queueTask(task);//-
        }//-
//-
        return { success: true };//-
      } else {//-
        throw new Error('Failed to generate component tasks');//-
      }//-
    } catch (err) {//-
      logger.error(`Component generation failed: ${err.message}`);//-
      return { success: false, error: err.message };//-
    }//-
  async processTask(task) {//+
    // Implement task processing logic//+
    logger.info(`Processing task: ${JSON.stringify(task)}`);//+
    // Add task execution logic here//+
  }
}//+

  /**//-
   * Write content to a file//-
   * @param {string} filePath - Path to write//-
   * @param {string} content - Content to write//-
   * @returns {object} - Success status and file path//-
   *///-
  async writeFile(filePath, content) {//-
    try {//-
      // Ensure we're writing within the project directory//-
      const normalizedPath = path.normalize(filePath);//-
      const projectRoot = process.cwd();//-
//-
      // Prevent path traversal attacks//-
      const absolutePath = path.resolve(projectRoot, normalizedPath);//-
      if (!absolutePath.startsWith(projectRoot)) {//-
        throw new Error(`Security violation: Path traversal attempt detected. Target: ${filePath}`);//-
      }//-
//-
      // Ensure directory exists//-
      const dir = path.dirname(absolutePath);//-
      await fs.mkdir(dir, { recursive: true });//-
//-
      // Write the file//-
      await fs.writeFile(absolutePath, content);//-
//-
      return { success: true, filePath };//-
    } catch (err) {//-
      logger.error(`Failed to write file ${filePath}: ${err.message}`);//-
      return { success: false, error: err.message };//-
    }//-
  }//-
//-
  /**//-
   * Analyze code quality//-
   * @param {string} target - Directory or file to analyze//-
   * @returns {object} - Success status//-
   *///-
  async analyzeCodeQuality(target) {//-
    try {//-
      // Use SonarQube if available//-
      if (this.availableTools.sonarqube) {//-
        logger.info(`Analyzing code quality for ${target} with SonarQube`);//-
        // In a real implementation, you would call SonarQube here//-
      } else {//-
        logger.info(`SonarQube not available, using basic analysis for ${target}`);//-
        // Perform basic analysis without SonarQube//-
      }//-
//-
      return { success: true };//-
    } catch (err) {//-
      logger.error(`Code quality analysis failed: ${err.message}`);//-
      return { success: false, error: err.message };//-
    }//-
  }//-
//-
  /**//-
   * Start the website build process//-
   * @returns {object} - Success status//-
   *///-
  async startWebsiteBuild() {//-
    logger.info("Starting website build process...");//-
    try {//-
      // Run the developer agent to design the website structure//-
      const result = await this.runPythonAgent("developer", "design_website_structure");//-
//-
      if (result && result.success) {//-
        logger.info("Website architecture generated");//-
//-
        // Queue up component generation tasks//-
        await this.queueTask({//-
          type: "generate-components",//-
          description: "Generate website components from architecture",//-
          data: {}//-
        });//-
//-
        return { success: true };//-
      } else {//-
        throw new Error("Failed to generate website architecture");//-
      }//-
    } catch (err) {//-
      logger.error(`Failed to start website build: ${err.message}`);//-
      return { success: false, error: err.message };//-
    }//-
  }//-
//-
  /**//-
   * Perform self-review of tool integrations//-
   * @returns {object} - Status of each tool//-
   *///-
  async selfReviewTools() {//-
    logger.info("Cherry performing comprehensive self-review of tool integrations...");//-
    const results = {//-
      n8n: false,//-
      sonarqube: false, //-
      cody: false//-
    };//-
//-
    // Check n8n with health check//-
    if (process.env.N8N_WEBHOOK_URL) {//-
      try {//-
        const response = await fetch(process.env.N8N_WEBHOOK_URL, {//-
          method: "HEAD"//-
        }).catch(() => ({ ok: false }));//-
//-
        results.n8n = response.ok;//-
//-
        if (results.n8n) {//-
          logger.info("n8n webhook is healthy");//-
        } else {//-
          logger.error("n8n health check failed");//-
        }//-
      } catch (err) {//-
        logger.error("n8n health check error: " + err.message);//-
      }//-
    }//-
//-
    // Check SonarQube//-
    const checkSonarQube = new Promise((resolve) => {//-
      exec("pgrep -f sonarqube", (error, stdout, stderr) => {//-
        if (error || !stdout.trim()) {//-
          logger.error("SonarQube process not detected. Attempting restart...");//-
          exec(//-
            process.env.SONARQUBE_START_CMD || "docker start sonarqube_container",//-
            (err) => {//-
              if (err) {//-
                logger.error("Failed to restart SonarQube: " + err.message);//-
              } else {//-
                logger.info("SonarQube restarted successfully.");//-
                results.sonarqube = true;//-
              }//-
              resolve();//-
            }//-
          );//-
        } else {//-
          logger.info("SonarQube is running fine.");//-
          results.sonarqube = true;//-
          resolve();//-
        }//-
      });//-
    });//-
//-
    // Check Cody extension//-
    const checkCody = new Promise((resolve) => {//-
      exec("code --list-extensions", (error, stdout, stderr) => {//-
        if (error) {//-
          logger.error("Failed to check VS Code extensions: " + error.message);//-
          resolve();//-
          return;//-
        }//-
//-
        const extensions = stdout.trim().split('\n');//-
        const codyInstalled = extensions.some(ext => //-
          ext.toLowerCase().includes('cody') || ext.includes('sourcegraph.cody-ai')//-
        );//-
//-
        results.cody = codyInstalled;//-
//-
        if (!codyInstalled) {//-
          logger.error("Cody VS Code extension not detected. Attempting to install...");//-
          exec(process.env.CODY_START_CMD || "code --install-extension sourcegraph.cody-ai", //-
            (err) => {//-
              if (err) logger.error("Failed to install Cody: " + err.message);//-
              else logger.info("Cody extension installation initiated");//-
              resolve();//-
            }//-
          );//-
        } else {//-
          logger.info("Cody VS Code extension is installed");//-
          resolve();//-
        }//-
      });//-
    });//-
//-
    // Wait for all checks to complete//-
    await Promise.all([checkSonarQube, checkCody]);//-
//-
    // Update Cherry's knowledge base with integration status//-
    this.knowledge_base.integrate({//-
      type: "tool_integration_status",//-
      data: results,//-
      timestamp: new Date().toISOString()//-
    });//-
//-
    return results;//-
  }//-
//-
  /**//-
   * Start periodic self-review interval//-
   * @returns {boolean} - Success status//-
   *///-
  startSelfReviewInterval() {//-
    // First immediate check//-
    this.selfReviewTools().then(results => {//-
      this.handleToolIntegrationReport(results);//-
    }).catch(err => {//-
      logger.error(`Self-review error: ${err.message}`);//-
    });//-
//-
    // Then periodic checks//-
    setInterval(() => {//-
      this.selfReviewTools().then(results => {//-
        this.handleToolIntegrationReport(results);//-
      }).catch(err => {//-
        logger.error(`Self-review error: ${err.message}`);//-
      });//-
    }, 300000); // 5 minutes//-
//-
    logger.info("Cherry's self-review monitoring initialized with 5-minute interval");//-
    return true;//-
  }//-
module.exports = AgentRunner;//+
>>>>>>> Tabnine >>>>>>>// {"source":"chat"}
  /**
   * Handle tool integration report
   * @param {object} results - Tool status results
   * @returns {boolean} - Success status
   */
  async handleToolIntegrationReport(results) {
    logger.info("Cherry analyzing tool integration results...");
    
    // Track which tools are available
    this.availableTools = {
      ...results
    };
    
    // Adjust strategy based on available tools
    if (results.sonarqube) {
      // If SonarQube is available, queue a task to analyze code quality
      this.queueTask({
        type: "analyze-code-quality",
        description: "Analyze code quality with SonarQube",
        data: {
          target: "src/"
        }
      });
    }
    
    return true;
  }
  
  /**
   * Optimize components
   * @param {array} componentNames - Array of component names
   * @returns {boolean} - Success status
   */
  async optimizeComponents(componentNames) {
    for (const name of componentNames) {
      try {
        // Sanitize component name to prevent command injection
        const safeName = name.replace(/[^\w-]/g, '');
        if (safeName !== name) {
          logger.warn(`Component name sanitized: ${name} -> ${safeName}`);
        }
        
        const result = await this.runPythonAgent("code_agent", "optimize_component", {
          component_path: `src/components/${safeName}.jsx`
        });
        
        if (result && result.success) {
          logger.info(`Optimized component: ${safeName}`);
        } else {
          logger.error(`Failed to optimize ${safeName}: ${result?.error || 'Unknown error'}`);
        }
      } catch (err) {
        logger.error(`Failed to optimize ${name}: ${err.message}`);
      }
    }
    return true;
  }
  
  /**
   * Add architectural signatures to code
   * @param {string} code - Code to modify
   * @returns {string} - Modified code
   */
  async add_architectural_signatures(code) {
    // Implementation for developer agent
    return code.replace(/architecture/g, "cherryArchitecture");
  }
  
  /**
   * Add optimization signatures to code
   * @param {string} code - Code to modify
   * @returns {string} - Modified code
   */
  async add_optimization_signatures(code) {
    // Implementation for code_agent
    return code.replace(/optimize/g, "cherryOptimize");
  }
  
  /**
   * Add component signatures to code
   * @param {string} code - Code to modify
   * @returns {string} - Modified code
   */
  async add_component_signatures(code) {
    // Implementation for code_generator
    return code.replace(/component/g, "cherryComponent");
  }
  
  /**
   * Scan code for security issues
   * @param {string} code - Code to scan
   * @returns {object} - Scan results
   */
  scanCodeForSecurityIssues(code) {
    const issues = [];
    
    // Check for sensitive patterns
    for (const pattern of this.sensitivePatterns) {
      pattern.lastIndex = 0; // Reset regex state
      let match;
      while ((match = pattern.exec(code)) !== null) {
        issues.push({
          type: 'sensitive_data',
          pattern: pattern.toString(),
          position: match.index,
          severity: 'high'
        });
      }
    }
    
    // Additional security checks could go here
    
    return {
      hasIssues: issues.length > 0,
      issues,
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = AgentRunner;
