import * as fs from 'fs';
import * as path from 'path';
import { secretsManager } from '../utils/secrets_manager';

/**
 * Configuration loader that processes JSON config files and resolves secrets
 */
export class ConfigLoader {
  /**
   * Load and process a configuration file
   * @param configPath Path to the configuration file
   * @returns Processed configuration object with secrets resolved
   */
  public static async loadConfig<T>(configPath: string): Promise<T> {
    try {
      // Read the config file
      const configContent = fs.readFileSync(configPath, 'utf8');
      
      // Process the configuration to replace secret references
      const processedConfig = await this.processConfig(configContent);
      
      return JSON.parse(processedConfig) as T;
    } catch (error) {
      console.error(`Error loading configuration from ${configPath}:`, error);
      throw error;
    }
  }

  /**
   * Process configuration content and resolve secret references
   * @param configContent Raw configuration content
   * @returns Processed configuration with secrets resolved
   */
  private static async processConfig(configContent: string): Promise<string> {
    // Resolve secret references in the configuration
    return secretsManager.resolveSecretReferences(configContent);
  }

  /**
   * Save a configuration with secret references
   * @param config Configuration object
   * @param configPath Path to save the configuration
   * @param replaceSecrets Whether to replace actual secrets with references
   */
  public static async saveConfig<T>(config: T, configPath: string, replaceSecrets = false): Promise<void> {
    try {
      let configContent = JSON.stringify(config, null, 4);

      // Ensure directory exists
      const configDir = path.dirname(configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }

      // Write the config file
      fs.writeFileSync(configPath, configContent, 'utf8');
    } catch (error) {
      console.error(`Error saving configuration to ${configPath}:`, error);
      throw error;
    }
  }
}
