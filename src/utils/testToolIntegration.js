const { exec } = require("child_process");
const logger = require("../logger");
const AgentRunner = require("../agents/agentRunner");
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));

async function testToolIntegration() {
  logger.info("Starting tool integration test...");

  const cherry = new AgentRunner({ agentName: "cherry-test" });

  // Enhance results to include GitHub apps
  const results = {
    ...(await cherry.selfReviewTools()),
    githubApps: {
      coderabbit: false,
    },
  };

  // Check CodeRabbit GitHub app integration
  if (process.env.GITHUB_TOKEN && process.env.GITHUB_REPO) {
    try {
      const [owner, repo] = process.env.GITHUB_REPO.split("/");

      const response = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/installations`,
        {
          headers: {
            Authorization: `token ${process.env.GITHUB_TOKEN}`,
            Accept: "application/vnd.github.v3+json",
          },
        }
      );

      if (response.ok) {
        const apps = await response.json();
        // Look for CodeRabbit in installed apps
        const coderabbitApp = apps.find(
          (app) =>
            app.app_slug === "coderabbit" ||
            app.app_id === process.env.CODERABBIT_APP_ID ||
            app.app_slug?.includes("coderabbit")
        );

        if (coderabbitApp) {
          logger.info("CodeRabbit GitHub app is installed and active");
          results.githubApps.coderabbit = true;
        } else {
          logger.error(
            "CodeRabbit GitHub app not detected in repository installations"
          );
        }
      } else {
        logger.error(
          `Failed to check GitHub apps: ${response.status} ${response.statusText}`
        );
      }
    } catch (err) {
      logger.error(`Error checking GitHub integrations: ${err.message}`);
    }
  } else {
    logger.warn(
      "GitHub token or repo not configured - skipping GitHub app checks"
    );
  }

  logger.info("Tool integration test results:");
  logger.info(JSON.stringify(results, null, 2));

  // Check and report offline tools including GitHub apps
  const offlineTools = [
    ...Object.entries(results)
      .filter(([key, status]) => key !== "githubApps" && !status)
      .map(([tool]) => tool),
    ...Object.entries(results.githubApps || {})
      .filter(([_, status]) => !status)
      .map(([app]) => `github-${app}`),
  ];

  if (offlineTools.length > 0) {
    logger.error(`The following tools are offline: ${offlineTools.join(", ")}`);
    logger.info(
      "Please check your configuration and verify tool installations."
    );
  } else {
    logger.info("All tools are operational!");
  }
}

testToolIntegration().catch((err) => {
  logger.error(`Test failed: ${err.message}`);
  process.exit(1);
});
