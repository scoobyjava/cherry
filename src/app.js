const express = require("express");
const aiderCodexRoutes = require("./routes/aiderCodexRoutes");

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Mount the Aider-Codex routes
app.use("/api/aider-codex", aiderCodexRoutes);

// Display welcome message on server start
function displayWelcomeMessage() {
  console.log("Welcome to Cherry - Code Analysis Tool");
  console.log("---------------------------------------");
  console.log("Available commands:");
  console.log("- npm start: Run the main application");
  console.log("- npm run analyze-complexity -- --file [filepath]: Analyze file complexity");
  console.log("- npm run sonar:start: Start SonarQube containers");
  console.log("- npm run sonar:stop: Stop SonarQube containers");
  console.log("- npm run sonar: Run SonarQube analysis");
}

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Server error" });
});

// Server configuration
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log("Cherry project is running!");
  displayWelcomeMessage();
});