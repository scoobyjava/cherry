import * as dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';

// Load environment variables from .env file if present
dotenv.config();

/**
 * Secret provider types supported by the application
 */
export enum SecretProviderType {
  ENV_VAR = 'env_var',
  AWS_SECRETS_MANAGER = 'aws_secrets_manager',
  GCP_SECRET_MANAGER = 'gcp_secret_manager',
  VAULT = 'vault',
  FILE = 'file'
}

/**
 * Configuration for secret providers
 */
interface SecretProviderConfig {
  type: SecretProviderType;
  options?: Record<string, any>;
}

/**
 * Class for managing secrets across different providers
 */
export class SecretsManager {
  private static instance: SecretsManager;
  private providers: Map<SecretProviderType, SecretProvider> = new Map();
  private defaultProvider: SecretProviderType = SecretProviderType.ENV_VAR;

  private constructor() {
    // Initialize the environment variables provider by default
    this.registerProvider(SecretProviderType.ENV_VAR, new EnvVarSecretProvider());
    this.registerProvider(SecretProviderType.FILE, new FileSecretProvider());
    
    // Additional providers can be registered as needed
  }

  /**
   * Get the singleton instance of SecretsManager
   */
  public static getInstance(): SecretsManager {
    if (!SecretsManager.instance) {
      SecretsManager.instance = new SecretsManager();
    }
    return SecretsManager.instance;
  }

  /**
   * Register a secret provider
   */
  public registerProvider(type: SecretProviderType, provider: SecretProvider): void {
    this.providers.set(type, provider);
  }

  /**
   * Set the default provider to use when no provider is specified
   */
  public setDefaultProvider(type: SecretProviderType): void {
    if (!this.providers.has(type)) {
      throw new Error(`Provider ${type} not registered`);
    }
    this.defaultProvider = type;
  }

  /**
   * Get a secret using the specified provider or the default one
   */
  public async getSecret(key: string, providerType?: SecretProviderType): Promise<string | null> {
    const type = providerType || this.defaultProvider;
    const provider = this.providers.get(type);
    
    if (!provider) {
      throw new Error(`Secret provider ${type} not found`);
    }
    
    return provider.getSecret(key);
  }

  /**
   * Parse secret references in a string and replace them with actual values
   * Format: ${SECRET:key:provider}
   */
  public async resolveSecretReferences(text: string): Promise<string> {
    const secretRefRegex = /\${SECRET:([^:}]+)(?::([^}]+))?}/g;
    let result = text;
    let match;
    
    // Create a copy to avoid modifying during iteration
    const matches = [...text.matchAll(secretRefRegex)];
    
    for (match of matches) {
      const [fullMatch, secretKey, providerType] = match;
      const provider = providerType ? 
        (Object.values(SecretProviderType).includes(providerType as SecretProviderType) ? 
          providerType as SecretProviderType : undefined) : 
        undefined;
      
      const secretValue = await this.getSecret(secretKey, provider);
      if (secretValue !== null) {
        result = result.replace(fullMatch, secretValue);
      }
    }
    
    return result;
  }
}

/**
 * Interface for secret providers
 */
interface SecretProvider {
  getSecret(key: string): Promise<string | null>;
}

/**
 * Environment variable secret provider
 */
class EnvVarSecretProvider implements SecretProvider {
  async getSecret(key: string): Promise<string | null> {
    return process.env[key] || null;
  }
}

/**
 * File-based secret provider
 */
class FileSecretProvider implements SecretProvider {
  private secretsDir = process.env.SECRETS_DIR || '/run/secrets';
  
  async getSecret(key: string): Promise<string | null> {
    try {
      const filePath = path.join(this.secretsDir, key);
      if (fs.existsSync(filePath)) {
        return fs.readFileSync(filePath, 'utf8').trim();
      }
      return null;
    } catch (error) {
      console.error(`Error reading secret file for key ${key}:`, error);
      return null;
    }
  }
}

// Export singleton instance
export const secretsManager = SecretsManager.getInstance();
