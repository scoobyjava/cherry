const logger = require('../utils/unifiedLogger');
const { query } = require('../integrations/huggingfaceClient');
const memorySystem = require('../memory/memorySystem');

class CommandInterfaceAgent {
  constructor() {
    this.commandHistory = [];
    this.intentClassifier = 'facebook/bart-large-mnli'; // Zero-shot classification model
    this.commandEnhancer = 'tiiuae/falcon-7b-instruct'; // Better command understanding
  }
  
  async execute(params) {
    const { action, command, context } = params;
    
    switch(action) {
      case 'processCommand':
        return await this.processCommand(command, context);
      case 'suggestNextActions':
        return await this.suggestNextActions(context);
      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }
  
  async processCommand(command, context = {}) {
    // Store command in history
    this.commandHistory.push({
      command,
      timestamp: Date.now(),
      context
    });
    
    // Use Hugging Face for intent classification
    try {
      // Classify the command intent using zero-shot classification
      const intents = ['code_analysis', 'memory_query', 'system_status', 'agent_execution', 'help'];
      const intentClassification = await query(this.intentClassifier, {
        inputs: command,
        parameters: {
          candidate_labels: intents
        }
      });
      
      const topIntent = intentClassification.labels[0];
      logger.info('Command intent classified', { command, intent: topIntent });
      
      // Based on intent, enhance the command with additional context
      const enhancedCommand = await this.enhanceCommand(command, topIntent, context);
      
      // Store the enhanced understanding in memory
      await memorySystem.store('episodic', `command_${Date.now()}`, {
        type: 'command_processed',
        originalCommand: command,
        enhancedCommand,
        intent: topIntent,
        timestamp: new Date().toISOString()
      });
      
      return {
        intent: topIntent,
        enhancedCommand,
        response: `Processing '${topIntent}' command: ${command}`
      };
    } catch (error) {
      logger.error('Error processing command with Hugging Face', { error: error.message });
      // Fallback to basic command processing
      return {
        intent: 'unknown',
        enhancedCommand: command,
        response: `Processing command: ${command}`
      };
    }
  }
  
  async enhanceCommand(command, intent, context) {
    // Use more advanced model to understand and enhance the command
    try {
      const prompt = `
Context: The user is interacting with Cherry, an AI assistant.
Command intent: ${intent}
Additional context: ${JSON.stringify(context)}
Original command: "${command}"

Provide an enhanced version of this command with any implied parameters made explicit. Format as JSON:
`;

      const response = await query(this.commandEnhancer, {
        inputs: prompt,
        parameters: {
          max_new_tokens: 200,
          temperature: 0.3,
          return_full_text: false
        }
      });
      
      // Try to parse as JSON
      try {
        return JSON.parse(response);
      } catch (e) {
        // If parsing fails, return the raw response
        return { enhanced: response };
      }
    } catch (error) {
      logger.error('Error enhancing command', { error: error.message });
      return { enhanced: command };
    }