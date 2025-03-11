const { AgentOrchestrator } = require("./agentOrchestrator");
const logger = require("./unifiedLogger");
const fs = require("fs").promises;
const path = require("path");
const { promisify } = require("util");
const exec = promisify(require("child_process").exec);
const axios = require("axios");
const express = require("express");

// Create debug router instead of using undefined 'app'
const debugRouter = express.Router();

// Create the debug orchestrator instance
const debugOrchestrator = new AgentOrchestrator({
  maxConcurrent: 3, // Reduced for better performance
  cacheAge: 60 * 60 * 1000, // 1 hour cache
  serviceUrl: process.env.DEBUG_SERVICE_URL || null,
});

// NPM Guardian Agent - Prevents package.json issues
debugOrchestrator.registerAgent("NPMGuardian", async (params = {}) => {
  const { checkVulnerabilities = true, checkOutdated = true } = params;
  logger.info("NPM Guardian starting checks");

  const results = {
    issues: [],
    recommendations: [],
  };

  // Check for vulnerabilities
  if (checkVulnerabilities) {
    try {
      const { stdout } = await exec("npm audit --json");
      const auditData = JSON.parse(stdout);

      // Check for vulnerabilities
      const vulnCount = auditData.metadata?.vulnerabilities?.total || 0;
      if (vulnCount > 0) {
        const critical = auditData.metadata?.vulnerabilities?.critical || 0;
        const high = auditData.metadata?.vulnerabilities?.high || 0;

        results.issues.push({
          type: "security",
          severity: critical > 0 ? 9 : high > 0 ? 8 : 6,
          message: `Found ${vulnCount} vulnerabilities (${critical} critical, ${high} high)`,
          source: "npm audit",
        });

        results.recommendations.push({
          action: "Run npm audit fix to resolve vulnerabilities",
          command: "npm audit fix",
          autoFix: true,
        });
      }
    } catch (error) {
      logger.warn(`NPM audit check failed: ${error.message}`);
    }
  }

  return results;
});

// Simple code scanner that doesn't consume too many resources
debugOrchestrator.registerAgent("CodeScanner", async (params = {}) => {
  const { files = [], types = ["security"] } = params;
  logger.info(`Scanning ${files.length} files`);

  // Lightweight scan implementation
  const results = [];
  for (const file of files.slice(0, 50)) {
    // Limit file count for performance
    try {
      const content = await fs.readFile(file, "utf8");

      // Simple checks that won't crash
      if (types.includes("security")) {
        if (content.includes("eval(") || content.includes("exec(")) {
          results.push({
            file,
            severity: 8,
            message: "Potential security risk: Found eval() or exec()",
            line:
              content
                .split("\n")
                .findIndex(
                  (line) => line.includes("eval(") || line.includes("exec(")
                ) + 1,
          });
        }
      }
    } catch (err) {
      logger.warn(`Error scanning ${file}: ${err.message}`);
    }
  }

  return results;
});

// AI Code Reviewer Agent - Uses DeepSeek to review code
debugOrchestrator.registerAgent("AICodeReviewer", async (params) => {
  const { code, context } = params;

  try {
    // Call DeepSeek v3 API
    const response = await axios.post(
      "https://api.deepseek.ai/v1/analyze",
      {
        code,
        context,
        analysis_type: "code_review",
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.DEEPSEEK_API_KEY || "demo-key"}`,
          "Content-Type": "application/json",
        },
      }
    );

    return {
      suggestions: response.data.suggestions || [],
      quality_score: response.data.quality_score || 0,
      improvement_areas: response.data.improvement_areas || [],
    };
  } catch (error) {
    logger.error("AI review error:", error.message);
    return {
      error: "Failed to perform AI review",
      suggestions: [],
    };
  }
});

// Error Analyzer Agent - Analyze runtime errors
debugOrchestrator.registerAgent("ErrorAnalyzer", async (params) => {
  const { error, stack, time } = params;

  try {
    logger.info(`Analyzing error: ${error.message}`);

    return {
      errorType: error.name || "Unknown",
      message: error.message,
      timestamp: time,
      analysis: "Error analysis will be implemented in next phase",
      recommendations: ["Check for null references", "Verify input validation"],
    };
  } catch (analyzeError) {
    logger.error("Error in error analyzer:", analyzeError.message);
    return {
      error: "Failed to analyze error",
      errorMessage: error.message,
    };
  }
});

// Helper function to generate NPM recommendations
function generateNpmRecommendations(audit, outdated) {
  const recommendations = [];

  // Security recommendations
  if (
    audit.metadata?.vulnerabilities?.high > 0 ||
    audit.metadata?.vulnerabilities?.critical > 0
  ) {
    recommendations.push({
      priority: "critical",
      action:
        "Run `npm audit fix` immediately to address security vulnerabilities",
      automated: true,
      command: "npm audit fix",
    });
  }

  // Handle outdated dependencies
  const majorOutdated = Object.entries(outdated || {}).filter(
    ([_, info]) =>
      info.current &&
      info.latest &&
      parseInt(info.latest.split(".")[0]) > parseInt(info.current.split(".")[0])
  );

  if (majorOutdated.length > 0) {
    recommendations.push({
      priority: "high",
      action: `Update ${majorOutdated.length} major version dependencies (breaking changes likely)`,
      automated: false,
      details: majorOutdated.map(
        ([pkg, info]) => `${pkg}: ${info.current} → ${info.latest}`
      ),
    });
  }

  return recommendations;
}

// Setup function for pre-commit checks
function setupPreCommitHook() {
  const hookScript = `#!/usr/bin/env node
try {
  const { execSync } = require('child_process');
  const path = require('path');
  
  // Get staged files
  const stagedFiles = execSync('git diff --staged --name-only')
    .toString()
    .split('\\n')
    .filter(Boolean);
  
  if (stagedFiles.length === 0) {
    console.log('No files to check');
    process.exit(0);
  }
  
  console.log('Pre-commit check: Running security scan...');
  
  // Simple security checks instead of calling back to orchestrator
  const securityIssues = [];
  
  for (const file of stagedFiles) {
    // Only check JS files to avoid overhead
    if (file.endsWith('.js') || file.endsWith('.ts')) {
      try {
        const content = require('fs').readFileSync(file, 'utf8');
        if (content.includes('eval(') || 
            content.includes('exec(') || 
            content.includes('password = "')) {
          securityIssues.push({
            file,
            message: "Security concern: eval/exec or hardcoded credentials"
          });
        }
      } catch (err) {
        console.warn(\`Couldn't check \${file}: \${err.message}\`);
      }
    }
  }
  
  if (securityIssues.length > 0) {
    console.error("Critical issues found in your changes:");
    securityIssues.forEach(issue => {
      console.error(\`- \${issue.file}: \${issue.message}\`);
    });
    process.exit(1);
  }
  
  process.exit(0);
} catch (err) {
  console.error("Error in pre-commit check:", err);
  // Don't block commit on hook errors
  process.exit(0);
}`;

  try {
    // Create .git/hooks directory if it doesn't exist
    fs.mkdir(path.join(process.cwd(), ".git", "hooks"), { recursive: true })
      .then(() => {
        // Write the pre-commit hook script
        return fs.writeFile(
          path.join(process.cwd(), ".git", "hooks", "pre-commit"),
          hookScript,
          { mode: 0o755 }
        );
      })
      .then(() => {
        logger.info("Pre-commit hook installed successfully");
      })
      .catch((err) => {
        logger.error("Failed to install pre-commit hook:", err.message);
      });
  } catch (error) {
    logger.error("Error setting up pre-commit hook:", error.message);
  }
}

// Setup uncaught exception handler - PROPERLY WRAPPED
function setupErrorHandlers() {
  process.on("uncaughtException", (error) => {
    logger.error("Uncaught exception:", error);

    try {
      // Log error but don't use the orchestrator directly here
      // to avoid potential infinite loops
      const errorInfo = {
        message: error.message,
        stack: error.stack,
        time: new Date().toISOString(),
      };

      // Write to error log file instead of calling orchestrator
      fs.appendFile(
        path.join(process.cwd(), "error-log.json"),
        JSON.stringify(errorInfo) + "\n"
      ).catch(() => {});
    } catch (handlerError) {
      // Just log, don't do anything that could crash
    }
  });
}

// Define API endpoints on the router
debugRouter.post("/check-npm", async (req, res) => {
  try {
    const results = await debugOrchestrator.executeTask("NPMGuardian", {});
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

debugRouter.get("/status", (req, res) => {
  res.json({
    active: debugOrchestrator.activeTasks.size > 0,
    agents: Object.fromEntries(
      Array.from(debugOrchestrator.agents.keys()).map((name) => [
        name,
        { status: debugOrchestrator.agents.get(name)?.status || "unknown" },
      ])
    ),
    tasks: {
      active: debugOrchestrator.activeTasks.size,
      pending: debugOrchestrator.pendingTasks?.length || 0,
    },
  });
});

// Set up error handlers
setupErrorHandlers();

// Only set up pre-commit hook in development
if (process.env.NODE_ENV === "development") {
  setupPreCommitHook();
}

// Export the debug orchestrator and setup functions
module.exports = {
  debugOrchestrator,
  debugRouter,
  setupPreCommitHook,
  setupErrorHandlers,
};
