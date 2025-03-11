const express = require("express");
const aiderCodexRoutes = require("./routes/aiderCodexRoutes");
const { debugRouter, setupErrorHandlers } = require("./utils/debugTeam");

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true, limit: "10mb" }));

// Mount the Aider-Codex routes
app.use("/api/aider-codex", aiderCodexRoutes);

// Add debug team API routes
app.use("/api/debug", debugRouter);

// Display welcome message on server start
function displayWelcomeMessage() {
  console.log("Welcome to Cherry - Code Analysis Tool");
  console.log("---------------------------------------");
  console.log("Available commands:");
  console.log("- npm start: Run the main application");
  console.log(
    "- npm run analyze-complexity -- --file [filepath]: Analyze file complexity"
  );
  console.log("- npm run sonar:start: Start SonarQube containers");
  console.log("- npm run sonar:stop: Stop SonarQube containers");
  console.log("- npm run sonar: Run SonarQube analysis");
}

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Server error" });
});

// Set up error handlers
setupErrorHandlers();

// Only set up pre-commit hook in development when explicitly requested
// to avoid performance issues in Codespaces
if (process.env.SETUP_GIT_HOOKS === "true") {
  const { setupPreCommitHook } = require("./utils/debugTeam");
  setupPreCommitHook();
}

// Server configuration
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log("Cherry project is running!");
  displayWelcomeMessage();
});

{
  "name": "Cherry Development",
  "customizations": {
    "vscode": {
      "settings": {
        "files.exclude": {
          "node_modules": true,
          ".git": true
        },
        "search.exclude": {
          "**/node_modules": true,
          "**/dist": true
        },
        "editor.formatOnSave": false,
        "typescript.disableAutomaticTypeAcquisition": true,
        "npm.autoDetect": "off",
        "javascript.updateImportsOnFileMove.enabled": "never",
        "typescript.surveys.enabled": false
      },
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ]
    }
  },
  "postCreateCommand": "npm install",
  "remoteUser": "node"
}

# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build output
dist/
build/
coverage/
.npmrc

# VSCode
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# Codespaces temp
.env
.DS_Store
.cache/
.npm/

fund=false
audit=false
save-exact=true
