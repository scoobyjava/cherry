import { VectorQuery, VectorResult, DatabaseQuery } from '../types';

/**
 * Mock implementation of Pinecone vector database for testing
 */
export class MockPineconeService {
  private vectors: Map<string, any[]> = new Map();

  constructor(private config: any = {}) {
    // Initialize with empty vectors for each namespace from config
    if (config.namespaces) {
      Object.keys(config.namespaces).forEach(namespace => {
        this.vectors.set(namespace, []);
      });
    }
  }

  async query(namespace: string, query: VectorQuery): Promise<VectorResult[]> {
    const topK = query.topK || this.getDefaultTopK(namespace);
    // Return mock results
    return Array(topK).fill(null).map((_, i) => ({
      id: `mock-id-${i}`,
      score: 1.0 - (i * 0.1),
      metadata: this.generateMockMetadata(namespace)
    }));
  }

  private getDefaultTopK(namespace: string): number {
    if (this.config.namespaces?.[namespace]?.default_top_k) {
      return this.config.namespaces[namespace].default_top_k;
    }
    return this.config.default_top_k || 5;
  }

  private generateMockMetadata(namespace: string): Record<string, any> {
    // Generate appropriate mock metadata based on namespace schema
    switch (namespace) {
      case 'search_agent':
        return {
          source_type: 'web',
          timestamp: Date.now(),
          relevance_score: 0.95,
          category: 'technology'
        };
      case 'recommendation_agent':
        return {
          user_id: 'test-user',
          item_id: 'test-item',
          interaction_type: 'click',
          timestamp: Date.now()
        };
      case 'qa_agent':
        return {
          document_id: 'test-doc',
          section_id: 'intro',
          confidence: 0.92,
          last_updated: Date.now()
        };
      default:
        return {};
    }
  }
}

/**
 * Mock implementation of PostgreSQL database for testing
 */
export class MockPostgresService {
  private data: Map<string, any[]> = new Map();

  async query(sql: string, params: any[] = []): Promise<any[]> {
    // Simple mock implementation that parses the SQL to decide what to return
    if (sql.toLowerCase().includes('select')) {
      const tableName = this.extractTableName(sql);
      return this.data.get(tableName) || [];
    }
    return [];
  }

  setMockData(tableName: string, data: any[]): void {
    this.data.set(tableName, data);
  }

  private extractTableName(sql: string): string {
    // Very simplistic SQL parser - in a real implementation this would be more robust
    const matches = sql.match(/from\s+([a-z0-9_]+)/i);
    return matches?.[1] || 'unknown';
  }
}

/**
 * Mock implementation of OpenAI service for testing
 */
export class MockOpenAIService {
  constructor(private config: any = {}) {}

  async complete(prompt: string, options: any = {}): Promise<string> {
    // Return deterministic responses based on prompt content
    if (prompt.includes('weather')) {
      return "The weather is sunny and 72 degrees.";
    } else if (prompt.includes('recommendation')) {
      return "I recommend the following items based on your preferences...";
    } else {
      return "This is a mock response from OpenAI service for testing purposes.";
    }
  }

  async embed(text: string): Promise<number[]> {
    // Return a deterministic mock embedding vector
    return Array(128).fill(0).map((_, i) => Math.sin(i));
  }
}
