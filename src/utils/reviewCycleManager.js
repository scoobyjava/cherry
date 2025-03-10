const AgentOrchestrator = require('./agentOrchestrator');
const prompts = require('../prompts/reviewCycle');
const logger = require('./unifiedLogger');

class ReviewCycleManager {
  constructor(config = {}) {
    this.orchestrator = new AgentOrchestrator();
    this.maxIterations = config.maxIterations || 3;
    this.qualityThreshold = config.qualityThreshold || 85;
    this.setupAgents();
    this.reviewHistory = new Map(); // Track review cycles by file
  }

  setupAgents() {
    // Register ReviewerAgent
    this.orchestrator.registerAgent('ReviewerAgent', async (params) => {
      const { code, context, type, originalCode, improvedCode, originalReview } = params;
      let prompt;
      
      switch (type) {
        case 'review':
          prompt = prompts.codeReview(code, context);
          break;
        case 'validate':
          prompt = prompts.validateImprovements(originalCode, improvedCode, originalReview);
          break;
        default:
          throw new Error(`Unknown ReviewerAgent task type: ${type}`);
      }
      
      // Execute review logic (would connect to LLM or other review system)
      logger.debug(`Executing ${type} review`, { codeLength: code?.length });
      return await this._executeReviewLogic(prompt);
    }, {
      timeout: 30000, // 30s timeout for reviews
      retries: 1
    });

    // Register Copilot agent
    this.orchestrator.registerAgent('Copilot', async (params) => {
      const { code, review, type, improvements, feedback, testResults } = params;
      let prompt;
      
      switch (type) {
        case 'improve':
          prompt = prompts.generateImprovements(code, review);
          break;
        case 'feedback':
          prompt = prompts.incorporateFeedback(code, improvements, feedback);
          break;
        case 'testfix':
          prompt = prompts.addressTestFailures(code, testResults);
          break;
        default:
          throw new Error(`Unknown Copilot task type: ${type}`);
      }
      
      // Execute improvement logic
      logger.debug(`Executing ${type} improvements`, { codeLength: code?.length });
      return await this._executeImprovementLogic(prompt);
    }, {
      timeout: 45000, // 45s timeout for code generation
      retries: 2
    });
  }

  async _executeReviewLogic(prompt) {
    // This would connect to your actual review implementation
    // Placeholder for demonstration
    return {
      functionality: { level: 'P1', issues: ['Function lacks input validation'] },
      performance: { level: 'P2', issues: ['Cache could be optimized'] },
      codeQuality: { level: 'P2', issues: ['Consider using destructuring assignment'] },
      security: { level: 'P0', issues: ['Potential memory leak in Promise handling'] },
      testing: { level: 'P1', issues: ['No error case tests'] }
    };
  }

  async _executeImprovementLogic(prompt) {
    // This would connect to your actual code improvement implementation
    // Placeholder for demonstration
    return {
      improvedCode: "// Improved code would be here\n// With security fixes\n// And better error handling",
      explanation: "Added input validation, fixed memory leak, improved error handling"
    };
  }

  async runIterativeReviewCycle(fileId, code, context = {}) {
    let currentCode = code;
    let iteration = 0;
    let finalReview = null;
    let improvements = [];
    
    logger.info(`Starting review cycle for ${fileId}`, { codeLength: code.length });
    
    try {
      while (iteration < this.maxIterations) {
        // Step 1: Get code review
        const review = await this.orchestrator.executeTask('ReviewerAgent', {
          code: currentCode,
          context,
          type: 'review'
        });
        
        // Save review for historical tracking
        if (!this.reviewHistory.has(fileId)) {
          this.reviewHistory.set(fileId, []);
        }
        this.reviewHistory.get(fileId).push({
          timestamp: Date.now(),
          review,
          iteration
        });
        
        // Check if we've reached acceptable quality
        const qualityScore = this._calculateQualityScore(review);
        if (qualityScore >= this.qualityThreshold) {
          logger.info(`Reached quality threshold: ${qualityScore}%`, { fileId, iteration });
          finalReview = review;
          break;
        }
        
        // Step 2: Generate improvements
        const improvement = await this.orchestrator.executeTask('Copilot', {
          code: currentCode,
          review,
          type: 'improve'
        });
        
        improvements.push({
          iteration,
          explanation: improvement.explanation
        });
        
        // Step 3: Validate improvements
        const validation = await this.orchestrator.executeTask('ReviewerAgent', {
          originalCode: currentCode,
          improvedCode: improvement.improvedCode,
          originalReview: review,
          type: 'validate'
        });
        
        // Only update if validation confirms improvement
        if (validation.improvementScore >= 50) {
          currentCode = improvement.improvedCode;
          logger.info(`Applied improvements at iteration ${iteration}`, { 
            score: validation.improvementScore,
            fileId
          });
        } else {
          logger.warn(`Improvements rejected at iteration ${iteration}`, {
            score: validation.improvementScore,
            fileId
          });
        }
        
        finalReview = validation;
        iteration++;
      }
      
      return {
        fileId,
        originalCode: code,
        improvedCode: currentCode,
        improvementSummary: improvements,
        finalReview,
        iterations: iteration,
        qualityScore: this._calculateQualityScore(finalReview)
      };
    } catch (error) {
      logger.error(`Review cycle failed for ${fileId}`, { error: error.message });
      throw error;
    }
  }

  async incorporateUserFeedback(fileId, currentCode, userFeedback) {
    logger.info(`Processing user feedback for ${fileId}`, {
      feedbackLength: userFeedback.length
    });
    
    try {
      const improvement = await this.orchestrator.executeTask('Copilot', {
        code: currentCode,
        feedback: userFeedback,
        type: 'feedback'
      });
      
      // Validate the user-feedback-based improvements
      const validation = await this.orchestrator.executeTask('ReviewerAgent', {
        originalCode: currentCode,
        improvedCode: improvement.improvedCode,
        type: 'validate'
      });
      
      return {
        fileId,
        originalCode: currentCode,
        improvedCode: improvement.improvedCode,
        explanation: improvement.explanation,
        validationScore: validation.improvementScore
      };
    } catch (error) {
      logger.error(`Failed to incorporate user feedback for ${fileId}`, {
        error: error.message
      });
      throw error;
    }
  }

  async fixFailingTests(fileId, currentCode, testResults) {
    logger.info(`Fixing failing tests for ${fileId}`, {
      failingTestCount: testResults.failures.length
    });
    
    try {
      const improvement = await this.orchestrator.executeTask('Copilot', {
        code: currentCode,
        testResults,
        type: 'testfix'
      });
      
      return {
        fileId,
        originalCode: currentCode,
        improvedCode: improvement.improvedCode,
        explanation: improvement.explanation
      };
    } catch (error) {
      logger.error(`Failed to fix tests for ${fileId}`, {
        error: error.message
      });
      throw error;
    }
  }

  _calculateQualityScore(review) {
    if (!review) return 0;
    
    // Convert priority levels to scores
    const priorityScores = {
      'P0': 0,  // Critical issues = 0 points
      'P1': 25, // High issues = 25 points
      'P2': 50, // Medium issues = 50 points
      'P3': 75  // Low issues = 75 points
    };
    
    // Calculate score based on highest priority issues in each category
    const scores = Object.values(review).map(category => 
      priorityScores[category.level] || 0
    );
    
    // Average the scores
    return scores.reduce((sum, score) => sum + score, 0) / scores.length;
  }
}

module.exports = ReviewCycleManager;