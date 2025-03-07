const fs = require("fs");
const path = require("path");

// Create a backup of the current file
function backupFile(filePath) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const backupPath = `${filePath}.backup-${timestamp}`;
  try {
    fs.copyFileSync(filePath, backupPath);
    console.log(`Backup created at: ${backupPath}`);
    return true;
  } catch (error) {
    console.error(`Failed to create backup: ${error.message}`);
    return false;
  }
}

// Multi-agent system definition
const agents = {
  securityAgent: {
    name: "Security Expert",
    description: "Identifies and fixes security vulnerabilities",
    patterns: {
      "eval\\s*\\(": (code) => code.replace(/eval\s*\(/g, "safe_eval("),
      innerHTML: (code) => code.replace(/\.innerHTML\s*=/g, ".textContent ="),
      "document\\.write": (code) =>
        code.replace(/document\.write\(/g, "safeDocumentWrite("),
    },
    weight: 0.9, // Security is high priority
  },

  performanceAgent: {
    name: "Performance Optimizer",
    description: "Improves code efficiency and speed",
    patterns: {
      "callback\\(": (code) => code.replace(/callback\(/g, "awaitFunction("),
      "for\\s*\\(var": (code) => code.replace(/for\s*\(var /g, "for (let "),
      "Array\\.concat": (code) => code.replace(/Array\.concat/g, "[...array]"),
    },
    weight: 0.75,
  },

  readabilityAgent: {
    name: "Readability Enhancer",
    description: "Improves code readability and maintainability",
    patterns: {
      "function\\s*\\(\\)\\s*{\\s*return": (code) =>
        code.replace(/function\s*\(\)\s*{\s*return\s*(.*?);\s*}/g, "() => $1"),
      "var\\s+": (code) => code.replace(/var\s+/g, "let "),
      "if\\s*\\(.+\\)\\s*{\\s*return true;\\s*}\\s*else\\s*{\\s*return false;\\s*}":
        (code) =>
          code.replace(
            /if\s*\((.+)\)\s*{\s*return true;\s*}\s*else\s*{\s*return false;\s*}/g,
            "return !!($1)"
          ),
    },
    weight: 0.6,
  },
};

// Learning system for pattern discovery
const learningSystem = {
  patternDatabase: new Map(),
  successMetrics: new Map(),

  recordSuccess(pattern, improvement) {
    if (!this.successMetrics.has(pattern)) {
      this.successMetrics.set(pattern, { uses: 0, improvements: 0 });
    }
    const metric = this.successMetrics.get(pattern);
    metric.uses++;
    metric.improvements += improvement;

    console.log(
      `Learning: Pattern "${pattern}" now has success rate of ${
        metric.improvements / metric.uses
      }`
    );
  },

  getTopPatterns() {
    return Array.from(this.successMetrics.entries())
      .sort(
        (a, b) => b[1].improvements / b[1].uses - a[1].improvements / a[1].uses
      )
      .slice(0, 5)
      .map(([pattern]) => pattern);
  },

  savePatterns() {
    const dataToSave = JSON.stringify(
      Array.from(this.successMetrics.entries())
    );
    fs.writeFileSync(
      path.join(__dirname, "learning-patterns.json"),
      dataToSave
    );
  },

  loadPatterns() {
    try {
      const data = fs.readFileSync(
        path.join(__dirname, "learning-patterns.json"),
        "utf8"
      );
      const entries = JSON.parse(data);
      this.successMetrics = new Map(entries);
    } catch (e) {
      console.log("No previous learning data found. Starting fresh.");
    }
  },
};

// Consensus mechanism to resolve competing suggestions
function buildConsensus(suggestions) {
  // Sort suggestions by agent weight * improvement score
  const rankedSuggestions = suggestions
    .map((s) => ({
      ...s,
      score: s.agentWeight * (s.improvement || 1),
    }))
    .sort((a, b) => b.score - a.score);

  // Take the top suggestions that don't conflict
  const selectedSuggestions = [];
  const modifiedRanges = new Set();

  for (const suggestion of rankedSuggestions) {
    // Simple conflict detection - check if ranges overlap
    const hasConflict = Array.from(modifiedRanges).some(
      (range) =>
        (suggestion.range[0] >= range[0] && suggestion.range[0] <= range[1]) ||
        (suggestion.range[1] >= range[0] && suggestion.range[1] <= range[1])
    );

    if (!hasConflict) {
      selectedSuggestions.push(suggestion);
      modifiedRanges.add(suggestion.range);
    }
  }

  return selectedSuggestions;
}

// Enhanced auto-refactor function using our agent system
function autoRefactor(sourcePath, issues) {
  // Create backup of the file we're about to change
  backupFile(sourcePath);

  // Load saved learning patterns
  learningSystem.loadPatterns();

  let code = fs.readFileSync(sourcePath, "utf8");
  let refactoredCode = code;

  // Collect all suggestions from agents
  const allSuggestions = [];

  // Process issues through our agent system
  issues.forEach((issue) => {
    // Find all agents that can handle this issue
    Object.entries(agents).forEach(([agentId, agent]) => {
      // Check if this agent has a pattern for this issue
      const transformer = agent.patterns[issue.pattern];
      if (transformer) {
        // Apply transformation
        const transformed = transformer(refactoredCode);

        // If there was a change, record the suggestion
        if (transformed !== refactoredCode) {
          allSuggestions.push({
            agentId,
            agentName: agent.name,
            agentWeight: agent.weight,
            pattern: issue.pattern,
            range: [
              issue.range?.start || 0,
              issue.range?.end || refactoredCode.length,
            ],
            transformation: transformed,
            improvement: 1.0, // Basic improvement score
          });
        }
      }
    });
  });

  // Build consensus among suggestions
  const selectedSuggestions = buildConsensus(allSuggestions);

  // Apply the winning transformations
  if (selectedSuggestions.length > 0) {
    // Sort in reverse order to avoid position shifting
    selectedSuggestions
      .sort((a, b) => b.range[0] - a.range[0])
      .forEach((suggestion) => {
        refactoredCode = suggestion.transformation;

        // Record success for learning
        learningSystem.recordSuccess(suggestion.pattern, 1.0);

        console.log(
          `Applied suggestion from ${suggestion.agentName} agent: ${suggestion.pattern}`
        );
      });

    // Save what we've learned
    learningSystem.savePatterns();
  }

  return refactoredCode;
}

// Compatibility with original version
const refactorings = {
  security_issue: agents.securityAgent.patterns,
  quality_issue: {
    ...agents.performanceAgent.patterns,
    ...agents.readabilityAgent.patterns,
  },
};

module.exports = { autoRefactor };

// Apply changes to a file if run directly
if (require.main === module) {
  const [, , filePath, ...issueParts] = process.argv;
  if (filePath) {
    const issues = issueParts.map((part) => {
      const [type, pattern] = part.split(":");
      return { type, pattern };
    });

    if (issues.length > 0) {
      const refactored = autoRefactor(filePath, issues);
      fs.writeFileSync(filePath, refactored);
      console.log(`Refactored ${filePath} with ${issues.length} issues`);
    } else {
      console.log("No issues specified for refactoring");
    }
  } else {
    console.log(
      "Usage: node auto-refactor.js <file-path> <issue-type>:<pattern> ..."
    );
  }
}
