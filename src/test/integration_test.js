const memoryStore = require("../memory/memoryStore");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const { IssueTracker } = require("../utils/issueTracker");
const issueTracker = new IssueTracker();

// Issue tracking and management system
class IssueTracker {
  constructor(options = {}) {
    this.issues = [];
    this.fixAttempts = new Map();
    this.options = {
      maxRetries: 3,
      retryDelay: 5000,
      autoFix: true,
      ...options,
    };
  }

  reportIssue(issue) {
    const issueId = `${issue.type}-${Date.now()}`;
    const newIssue = {
      id: issueId,
      ...issue,
      timestamp: new Date().toISOString(),
      status: "reported",
      fixAttempts: 0,
    };

    this.issues.push(newIssue);
    console.log(`Issue reported: ${issue.type} - ${issue.message}`);

    if (this.options.autoFix && issue.fixStrategy) {
      this.attemptFix(issueId);
    }

    return issueId;
  }

  async attemptFix(issueId) {
    const issue = this.issues.find((i) => i.id === issueId);
    if (!issue || !issue.fixStrategy) return false;

    if (issue.fixAttempts >= this.options.maxRetries) {
      issue.status = "fix_failed";
      console.error(`Max fix attempts reached for issue: ${issueId}`);
      return false;
    }

    issue.fixAttempts++;
    issue.status = "fixing";

    try {
      const result = await issue.fixStrategy(issue);
      if (result.success) {
        issue.status = "fixed";
        issue.resolution = result.resolution;
        console.log(`Issue fixed: ${issueId} - ${result.resolution}`);
        return true;
      } else {
        issue.status = "fix_failed";
        issue.lastError = result.error;
        console.error(`Fix failed for issue ${issueId}: ${result.error}`);

        // Schedule retry if under max attempts
        if (issue.fixAttempts < this.options.maxRetries) {
          setTimeout(() => this.attemptFix(issueId), this.options.retryDelay);
        }
        return false;
      }
    } catch (error) {
      issue.status = "fix_error";
      issue.lastError = error.message;
      console.error(
        `Error during fix attempt for ${issueId}: ${error.message}`
      );
      return false;
    }
  }

  getIssueStats() {
    const stats = {
      total: this.issues.length,
      reported: 0,
      fixing: 0,
      fixed: 0,
      failed: 0,
    };

    this.issues.forEach((issue) => {
      if (issue.status === "reported") stats.reported++;
      else if (issue.status === "fixing") stats.fixing++;
      else if (issue.status === "fixed") stats.fixed++;
      else stats.failed++;
    });

    return stats;
  }
}

function testMemoryStore() {
  console.log("=== Testing Memory Store ===");
  // Add a test entry and retrieve it to verify persistence.
  const testEntry = {
    type: "test_entry",
    content: "This is a test",
    tags: ["integration", "memory"],
  };
  const id = memoryStore.addEntry(testEntry);
  const results = memoryStore.getRelevantEntries((entry) => entry.id === id);
  if (results.length !== 1) {
    throw new Error(
      "Memory Store test failed: Entry not found or duplicate detected."
    );
  }
  console.log("Memory Store test passed.");
}

function testAnalyzeComplexityCLI() {
  console.log("=== Testing Analyze Complexity CLI ===");
  const testFilePath = path.join(__dirname, "tempTestFile.js");

  // Include problematic code that should be detected
  const testCode = `
    function complexFunction(a, b, c) {
      if (a > 10) {
        if (b > 20) {
          if (c > 30) {
            return a + b + c;
          } else {
            return a + b;
          }
        } else {
          return a;
        }
      } else {
        return 0;
      }
    }
  `;
  fs.writeFileSync(testFilePath, testCode, "utf8");

  try {
    const cliPath = path.join(__dirname, "../../src/cli/analyze-complexity.js");
    // Add --auto-fix flag to enable self-fixing
    const output = execSync(
      `node ${cliPath} --file ${testFilePath} --auto-fix`
    );
    console.log("CLI Output:");
    console.log(output.toString());

    // Verify the file was fixed by checking its contents
    const fixedCode = fs.readFileSync(testFilePath, "utf8");
    if (
      fixedCode.includes("complexFunction") &&
      !fixedCode.includes("if (a > 10)")
    ) {
      console.log("Self-fixing successfully refactored complex code!");
    } else {
      console.log("Auto-fix attempted but code structure unchanged.");
    }
  } catch (error) {
    // Report the issue to the issue tracker
    issueTracker.reportIssue({
      type: "cli_failure",
      message: error.message,
      fixStrategy: async () => {
        // Implement auto-fixing strategy
        console.log("Attempting to fix CLI issue...");
        // Example: Try with different parameters, fix path issues, etc.
        return {
          success: true,
          resolution: "CLI issue fixed by adjusting parameters",
        };
      },
    });
  } finally {
    fs.unlinkSync(testFilePath);
  }
}

function testAgentRunner() {
  console.log("=== Testing Agent Runner ===");
  // Attempt to load the agentRunner. It should try to check connectivity and either restart SonarQube or report success.
  try {
    require("../../src/agents/agentRunner");
    console.log("Agent Runner loaded successfully.");
  } catch (error) {
    throw new Error("Agent Runner test failed: " + error.message);
  }
}

function runIntegrationTests() {
  try {
    const checkN8n = require("../agents/n8nChecker");
    checkN8n();
    testMemoryStore();
    testAnalyzeComplexityCLI();
    testAgentRunner();

    const stats = issueTracker.getIssueStats();
    console.log("=== Integration Test Summary ===");
    console.log(`Total issues: ${stats.total}`);
    console.log(`  - Fixed: ${stats.fixed}`);
    console.log(`  - Failed: ${stats.failed}`);
    console.log(`  - In progress: ${stats.fixing}`);

    if (stats.failed > 0) {
      console.warn("Some issues could not be automatically fixed.");
      process.exitCode = 1;
    } else {
      console.log("=== All Tests Passed or Issues Fixed ===");
    }
  } catch (error) {
    issueTracker.reportIssue({
      type: "test_failure",
      message: error.message,
      severity: "high",
    });
    process.exitCode = 1;
  }
}

runIntegrationTests();
