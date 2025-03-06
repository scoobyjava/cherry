const fetch = require("node-fetch");

const logger = {
  info: (msg) => {
    console.log("[INFO]", msg);
  },
  error: (msg) => {
    console.error("[ERROR]", msg);
    // If an n8n webhook URL is provided in the environment,
    // "fire-and-forget" send the error details to n8n.
    if (process.env.N8N_WEBHOOK_URL) {
      fetch(process.env.N8N_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          level: "error",
          message: msg,
          timestamp: new Date().toISOString(),
        }),
      }).catch((err) => {
        console.error("[ERROR] Failed to send error to n8n:", err.message);
      });
    }
  },
};

module.exports = logger;
