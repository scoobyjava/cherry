const aiderCodexHandler = require("../agents/aiderCodexAgent");

// Add to your agents configuration
const agents = {
  // ... other agents
  "aider-codex": {
    handler: aiderCodexHandler,
    description: "Uses Aider-Codex to process and modify code based on natural language instructions",
    parameters: {
      prompt: "The instruction or query for code modifications",
      files: "Optional array of file paths to include in the context",
      context: "Optional additional context for the request",
      options: "Optional configuration options for Aider-Codex"
    }
  }
};

module.exports = agents;
