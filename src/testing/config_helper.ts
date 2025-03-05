import fs from 'fs';
import path from 'path';
import { DeepPartial } from '../types';

/**
 * Helper class for managing configuration in tests
 */
export class TestConfigManager {
  private originalConfig: any;
  private config: any;

  /**
   * Load a configuration file for testing
   * 
   * @param configPath Path to the configuration file
   */
  constructor(configPath: string) {
    try {
      const configContent = fs.readFileSync(configPath, 'utf-8');
      this.originalConfig = JSON.parse(configContent);
      this.config = JSON.parse(configContent);
    } catch (error) {
      console.error(`Failed to load config from ${configPath}:`, error);
      this.originalConfig = {};
      this.config = {};
    }
  }

  /**
   * Override specific configuration values for testing
   * 
   * @param overrides Partial configuration object with overrides
   */
  override<T extends object>(overrides: DeepPartial<T>): void {
    this.config = this.deepMerge(this.config, overrides);
  }

  /**
   * Reset configuration to original values
   */
  reset(): void {
    this.config = JSON.parse(JSON.stringify(this.originalConfig));
  }

  /**
   * Get current configuration
   */
  getConfig<T>(): T {
    return this.config as T;
  }

  /**
   * Helper method to deep merge objects
   */
  private deepMerge(target: any, source: any): any {
    const output = { ...target };