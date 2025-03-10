const {
  testConnection,
  initializeIndices,
} = require("../utils/elasticsearchClient");
const logger = require("../utils/unifiedLogger");

async function setup() {
  logger.info("Testing Elasticsearch connection...");
  const connected = await testConnection();

  if (connected) {
    logger.info("Initializing indices...");
    await initializeIndices();
    logger.info("Elasticsearch setup complete");
  } else {
    logger.error("Failed to connect to Elasticsearch");
    process.exit(1);
  }
}

setup().catch((err) => {
  logger.error("Setup failed", { error: err.message });
  process.exit(1);
});
