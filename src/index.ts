import { ConfigLoader } from './config/config_loader';
import * as path from 'path';

async function main() {
  try {
    // Load configuration with secrets resolved
    const config = await ConfigLoader.loadConfig(
      path.join(__dirname, '../benchmarks/benchmark_config.json')
    );
    
    console.log('Configuration loaded with secure secrets');
    
    // Use configuration (safely log non-sensitive parts only)
    console.log('Pinecone Environment:', config.pinecone.environment);
    console.log('Postgres Host:', config.postgres.host);
    console.log('OpenAI Default Model:', config.openai?.default_model);
    
    // Now you can use the configuration with resolved secrets
    // Example: initialize clients with secure API keys
    
  } catch (error) {
    console.error('Failed to load configuration:', error);
    process.exit(1);
  }
}

// Run the application
main().catch(console.error);
