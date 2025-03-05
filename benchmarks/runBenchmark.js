const path = require('path');
const { loadConfig } = require('../util/loadConfig');
const { validatePort, validateString } = require('../util/validation');

/**
 * Run benchmarks using the configuration
 */
async function runBenchmark() {
  try {
    // Load and validate the configuration
    const configPath = path.join(__dirname, 'benchmark_config.json');
    const config = loadConfig(configPath);
    
    console.log('Benchmark configuration loaded successfully');
    
    // Example of using validation for runtime parameters
    const port = process.env.BENCHMARK_PORT ? parseInt(process.env.BENCHMARK_PORT, 10) : 3000;
    if (!validatePort(port, config)) {
      throw new Error(`Invalid port number: ${port}. Must be between ${config.app.validation.port_ranges.min} and ${config.app.validation.port_ranges.max}`);
    }
    
    // Setup services with proper input validation
    await setupServices(config);
    
    // Run benchmarks
    console.log('Running benchmarks...');
    await runBenchmarkSuite(config);
    
    console.log('Benchmarks completed successfully');
  } catch (err) {
    console.error(`Benchmark failed: ${err.message}`);
    process.exit(1);
  }
}

/**
 * Setup services for benchmarking
 * @param {Object} config - The configuration object
 */
async function setupServices(config) {
  console.log('Setting up services for benchmarking...');
  
  // Setup Pinecone
  if (config.app.services.pinecone) {
    await setupPineconeService(config.app.services.pinecone);
  }
  
  // Setup other services...
}

/**
 * Setup Pinecone service
 * @param {Object} pineconeConfig - The Pinecone configuration
 */
async function setupPineconeService(pineconeConfig) {
  // Validate index name at runtime before using
  if (!validateString(pineconeConfig.index_name, { minLength: 1 })) {
    throw new Error('Invalid Pinecone index name');
  }
  
  console.log(`Setting up Pinecone with index: ${pineconeConfig.index_name}`);
  
  // Setup namespaces with validation
  if (pineconeConfig.namespaces) {
    for (const [namespace, nsConfig] of Object.entries(pineconeConfig.namespaces)) {
      console.log(`Setting up namespace: ${namespace}`);
      
      // Validate default_top_k before using
      const topK = nsConfig.default_top_k || pineconeConfig.default_top_k || 5;
      if (topK < 1 || topK > 1000 || !Number.isInteger(topK)) {
        throw new Error(`Invalid default_top_k for namespace ${namespace}: ${topK}`);
      }
      
      // Additional namespace setup...
    }
  }
}

/**
 * Run the benchmark suite
 * @param {Object} config - The configuration object
 */
async function runBenchmarkSuite(config) {
  // Implementation of benchmark suite with proper validation...
  console.log('Benchmark suite running with validated configuration');
}

// Run benchmarks if this file is executed directly
if (require.main === module) {
  runBenchmark().catch(err => {
    console.error('Unhandled error:', err);
    process.exit(1);
  });
}

module.exports = {
  runBenchmark
};
