// Use dynamic import for node-fetch instead of require
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const logger = {
  info: (msg) => {
    console.log(`[INFO] ${msg}`);
  },
  error: (msg) => {
    console.error(`[ERROR] ${msg}`);
    // n8n webhook operations if configured
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
  warn: (msg) => {
    console.warn(`[WARN] ${msg}`);
  }
};

module.exports = logger;
