const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const path = require("path");
const logger = require("../utils/unifiedLogger");

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Website generators
function generateHTML(name, theme) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${name}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>Welcome to ${name}!</h1>
  <p>Theme: ${theme}</p>
  <script src="script.js"></script>
</body>
</html>`;
}

function generateCSS(theme) {
  if (theme === "modern") {
    return "body { font-family: Arial, sans-serif; background-color: #f4f4f4; }";
  }
  return "body { font-family: serif; background-color: #ffffff; }";
}

function generateJS() {
  return 'console.log("Website loaded successfully.");';
}

// API endpoints
app.post("/api/command", async (req, res) => {
  const { command, params } = req.body;
  try {
    switch (command) {
      case "build_website": {
        const { name = "cherry-dashboard", theme = "modern" } = params;

        // Build the website files inside the public directory
        const websiteDir = path.join(__dirname, "../../public/website", name);
        fs.mkdirSync(websiteDir, { recursive: true });

        fs.writeFileSync(
          path.join(websiteDir, "index.html"),
          generateHTML(name, theme)
        );
        fs.writeFileSync(
          path.join(websiteDir, "styles.css"),
          generateCSS(theme)
        );
        fs.writeFileSync(path.join(websiteDir, "script.js"), generateJS());

        logger.info(`Website built successfully: ${name}`);

        return res.json({
          status: "success",
          message: "Website built successfully",
          url: `http://localhost:${port}/${name}/`,
        });
      }

      case "generate_component": {
        const { type, target = "cherry-dashboard" } = params;

        logger.info(`Component requested: ${type} for ${target}`);

        return res.json({
          status: "success",
          message: `Component ${type} requested (implementation pending)`,
          component: type,
        });
      }

      default:
        return res.status(400).json({ error: "Unknown command" });
    }
  } catch (error) {
    logger.error(`Error executing command: ${command}`, {
      error: error.message,
    });
    return res.status(500).json({ error: error.message });
  }
});

// Serve static files
app.use(express.static(path.join(__dirname, "../../public/website")));

// Start server
app.listen(port, () => {
  logger.info(`Cherry Command Center running at http://localhost:${port}`);
});
