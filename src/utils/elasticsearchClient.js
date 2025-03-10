const { Client } = require("@elastic/elasticsearch");
const logger = require("./unifiedLogger");
require("dotenv").config();

const client = new Client({
  node: process.env.ELASTICSEARCH_URL || "http://localhost:9200",
  auth:
    process.env.ELASTICSEARCH_USERNAME && process.env.ELASTICSEARCH_PASSWORD
      ? {
          username: process.env.ELASTICSEARCH_USERNAME,
          password: process.env.ELASTICSEARCH_PASSWORD,
        }
      : undefined,
});

// Test the connection
async function testConnection() {
  try {
    const info = await client.info();
    logger.info("Elasticsearch connected successfully", {
      version: info.version.number,
      cluster_name: info.cluster_name,
    });
    return true;
  } catch (error) {
    logger.error("Elasticsearch connection failed", {
      error: error.message,
    });
    return false;
  }
}

// Initialize indices for Cherry memory types
async function initializeIndices() {
  const indices = [
    {
      name: "cherry-episodic",
      mappings: {
        properties: {
          timestamp: { type: "date" },
          type: { type: "keyword" },
          content: { type: "text" },
          metadata: { type: "object", enabled: true },
          vector: { type: "dense_vector", dims: 768 },
        },
      },
    },
    {
      name: "cherry-semantic",
      mappings: {
        properties: {
          title: { type: "text" },
          content: { type: "text" },
          category: { type: "keyword" },
          timestamp: { type: "date" },
          vector: { type: "dense_vector", dims: 768 },
        },
      },
    },
    {
      name: "cherry-procedural",
      mappings: {
        properties: {
          name: { type: "text" },
          steps: { type: "text" },
          category: { type: "keyword" },
          last_used: { type: "date" },
          execution_count: { type: "integer" },
          vector: { type: "dense_vector", dims: 768 },
        },
      },
    },
  ];

  for (const index of indices) {
    try {
      const exists = await client.indices.exists({ index: index.name });

      if (!exists) {
        await client.indices.create({
          index: index.name,
          body: {
            mappings: index.mappings,
          },
        });
        logger.info(`Created index: ${index.name}`);
      } else {
        logger.info(`Index already exists: ${index.name}`);
      }
    } catch (error) {
      logger.error(`Error creating index ${index.name}`, {
        error: error.message,
      });
    }
  }
}

// Search functionality
async function semanticSearch(indexName, queryText, size = 10) {
  try {
    const result = await client.search({
      index: indexName,
      body: {
        query: {
          multi_match: {
            query: queryText,
            fields: ["title^2", "content", "steps"],
          },
        },
        size,
      },
    });

    return result.hits.hits.map((hit) => ({
      id: hit._id,
      score: hit._score,
      ...hit._source,
    }));
  } catch (error) {
    logger.error("Error performing semantic search", { error: error.message });
    throw error;
  }
}

// Store a document
async function storeDocument(indexName, document, id = undefined) {
  try {
    const params = {
      index: indexName,
      body: document,
    };

    if (id) {
      params.id = id;
    }

    const result = await client.index(params);
    logger.debug("Document stored successfully", {
      index: indexName,
      id: result._id,
    });

    return result._id;
  } catch (error) {
    logger.error("Error storing document", { error: error.message });
    throw error;
  }
}

// Initialize connection and indices
(async () => {
  const connected = await testConnection();
  if (connected) {
    await initializeIndices();
  }
})();

module.exports = {
  client,
  testConnection,
  semanticSearch,
  storeDocument,
  initializeIndices,
};
