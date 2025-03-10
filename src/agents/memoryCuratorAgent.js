const logger = require('../utils/unifiedLogger');
const { query } = require('../integrations/huggingfaceClient');
const memorySystem = require('../memory/memorySystem');

class MemoryCuratorAgent {
  constructor() {
    this.summaryModel = 'sshleifer/distilbart-cnn-12-6';
    this.embeddingModel = 'sentence-transformers/all-MiniLM-L6-v2';
    this.lastCurationTime = null;
  }
  
  async execute(params) {
    const { action } = params;
    
    switch(action) {
      case 'summarize_recent':
        return await this.summarizeRecentMemories();
      case 'curate_memories':
        return await this.curateMemories();
      case 'generate_insight':
        return await this.generateInsight(params.topic);
      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }
  
  async summarizeRecentMemories() {
    logger.info('Summarizing recent memories');
    
    try {
      // Get recent episodic memories
      const cutoffTime = new Date();
      cutoffTime.setHours(cutoffTime.getHours() - 24); // Last 24 hours
      
      const recentMemories = [];
      memorySystem.memory.episodic.forEach((entry, key) => {
        if (new Date(entry.metadata.createdAt) >= cutoffTime) {
          recentMemories.push({
            key,
            ...entry.data
          });
        }
      });
      
      if (recentMemories.length === 0) {
        return {
          success: true,
          message: 'No recent memories found to summarize',
          summary: null
        };
      }
      
      // Prepare memories for summarization
      const memoryTexts = recentMemories.map(memory => {
        let text = `Type: ${memory.type || 'unknown'}, `;
        
        if (memory.type === 'github_event') {
          text += `Event: ${memory.eventType}, Repo: ${memory.repository}`;
        } else if (memory.type === 'command_processed') {
          text += `Command: ${memory.originalCommand}`;
        } else if (memory.type === 'user_command') {
          text += `Command: ${memory.command}`;
        } else {
          // Generic approach for other memory types
          text += Object.entries(memory)
            .filter(([key]) => key !== 'key' && key !== 'data' && typeof memory[key] !== 'object')
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');
        }
        
        return text;
      });
      
      // Use Hugging Face to generate a summary
      const memoryContext = memoryTexts.join('\n');
      const summary = await query(this.summaryModel, {
        inputs: memoryContext,
        parameters: {
          max_length: 200,
          min_length: 50
        }
      });
      
      // Store the summary as a semantic memory
      const summaryId = await memorySystem.store(
        'semantic',
        `daily_summary_${new Date().toISOString().split('T')[0]}`,
        {
          type: 'daily_summary',
          summary,
          memoryCount: recentMemories.length,
          timestamp: new Date().toISOString()
        }
      );
      
      logger.info('Created memory summary', { summaryId });
      
      return {
        success: true,
        message: `Summarized ${recentMemories.length} recent memories`,
        summary
      };
      
    } catch (error) {
      logger.error('Error summarizing memories', { error: error.message });
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  async curateMemories() {
    logger.info('Curating memories');
    this.lastCurationTime = new Date();
    
    // Memory curation logic...
    return {
      success: true,
      message: 'Memory curation complete'
    };
  }
  
  async generateInsight(topic) {
    logger.info('Generating insight on topic', { topic });
    
    try {
      // Find relevant memories on the topic
      const relevantMemories = await memorySystem.search('semantic', topic);
      
      if (relevantMemories.length === 0) {
        return {
          success: true,
          message: `No memories found related to "${topic}"`,
          insight: null
        };
      }