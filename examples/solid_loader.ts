import * as fs from 'fs/promises';
import * as path from 'path';

// Interfaces following Interface Segregation Principle
interface ServiceConfig {
  version: string;
  implementation: string;
}

interface VectorDBConfig extends ServiceConfig {
  index_name: string;
  default_top_k: number;
  namespaces: Record<string, NamespaceConfig>;
}

interface NamespaceConfig {
  description: string;
  metadata_schema: Record<string, string>;
  default_top_k: number;
}

interface RelationalDBConfig extends ServiceConfig {
  database: string;
  query_settings: {
    statement_timeout_ms: number;
  };
}

interface AIProviderConfig extends ServiceConfig {
  default_model: string;
  max_tokens: number;
}

interface ConfigManifest {
  version: string;
  services: {
    vector_db: {
      implementation: string;
      config_path: string;
    };
    relational_db: {
      implementation: string;
      config_path: string;
    };
    ai_provider: {
      implementation: string;
      config_path: string;
    };
  };
  features_config_path: string;
  validation_config_path: string;
}

// Abstract factory following Dependency Inversion Principle
abstract class VectorDBService {
  abstract storeVectors(namespace: string, vectors: any[]): Promise<void>;
  abstract queryVectors(namespace: string, query: any, topK?: number): Promise<any[]>;
  abstract deleteVectors(namespace: string, ids: string[]): Promise<void>;
  abstract listNamespaces(): Promise<string[]>;
}

// Concrete implementation
class PineconeService extends VectorDBService {
  private config: VectorDBConfig;
  
  constructor(config: VectorDBConfig) {
    super();
    this.config = config;
  }

  async storeVectors(namespace: string, vectors: any[]): Promise<void> {
    console.log(`Storing vectors in Pinecone namespace ${namespace}`);
    // Implementation details...
  }

  async queryVectors(namespace: string, query: any, topK?: number): Promise<any[]> {
    const actualTopK = topK || 
      this.config.namespaces[namespace]?.default_top_k || 
      this.config.default_top_k;
    
    console.log(`Querying vectors from Pinecone namespace ${namespace} with top_k=${actualTopK}`);
    // Implementation details...
    return [];
  }

  async deleteVectors(namespace: string, ids: string[]): Promise<void> {
    console.log(`Deleting vectors from Pinecone namespace ${namespace}`);
    // Implementation details...
  }

  async listNamespaces(): Promise<string[]> {
    return Object.keys(this.config.namespaces);
  }
}

// Factory following Dependency Inversion Principle
class ServiceFactory {
  static async createVectorDBService(configPath: string): Promise<VectorDBService> {
    const config = JSON.parse(await fs.readFile(configPath, 'utf8')) as VectorDBConfig;
    
    switch(config.implementation) {
      case 'pinecone':
        return new PineconeService(config);
      // Could add more implementations here
      default:
        throw new Error(`Unknown vector DB implementation: ${config.implementation}`);
    }
  }
  
  // Additional factory methods for other service types...
}

// Configuration loader following Single Responsibility Principle
class ConfigLoader {
  private basePath: string;
  private manifest?: ConfigManifest;
  
  constructor(basePath: string) {
    this.basePath = basePath;
  }
  
  async loadManifest(): Promise<ConfigManifest> {
    if (!this.manifest) {
      const manifestPath = path.join(this.basePath, 'manifest.json');
      this.manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8')) as ConfigManifest;
    }
    return this.manifest;
  }
  
  async getServiceConfigPath(serviceType: keyof ConfigManifest['services']): Promise<string> {
    const manifest = await this.loadManifest();
    return path.join(this.basePath, manifest.services[serviceType].config_path);
  }
}

// Example usage
async function main() {
  // Set up configuration
  const configLoader = new ConfigLoader('./config');
  
  // Get vector DB service - notice we're programming to an interface, not an implementation
  const vectorDBConfigPath = await configLoader.getServiceConfigPath('vector_db');
  const vectorDBService: VectorDBService = await ServiceFactory.createVectorDBService(vectorDBConfigPath);
  
  // Use the service without knowing its concrete implementation
  const namespaces = await vectorDBService.listNamespaces();
  console.log(`Available namespaces: ${namespaces.join(', ')}`);
  
  // Perform a query
  const results = await vectorDBService.queryVectors('search_agent', { query: "example" });
  console.log(`Found ${results.length} results`);
}

main().catch(console.error);
