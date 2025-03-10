const { EventEmitter } = require("events");
const { AgentOrchestrator } = require("../agents/AgentOrchestrator");
const { MemoryManager } = require("../memory/MemoryManager");
const { Logger } = require("../utils/Logger");

/**
 * SimulationTester - Runs plan simulations in sandboxed environments to detect risks
 * before actual execution occurs.
 */
class SimulationTester {
  constructor(config = {}) {
    this.eventEmitter = new EventEmitter();
    this.logger = new Logger("SimulationTester");
    this.sandboxEnvironment = config.sandboxEnvironment || "isolated";
    this.maxSimulationSteps = config.maxSimulationSteps || 50;
    this.riskThresholds = config.riskThresholds || {
      high: 0.7,
      medium: 0.4,
      low: 0.2,
    };
  }

  /**
   * Simulates a multi-step plan to assess potential risks
   * @param {Object} plan - The execution plan to simulate
   * @returns {Object} Simulation results with risk assessment
   */
  async simulatePlan(plan) {
    this.logger.info(`Starting simulation for plan: ${plan.id}`);

    // Create sandbox environment
    const sandboxMemory = new MemoryManager({ mode: "ephemeral" });
    const sandboxOrchestrator = new AgentOrchestrator({
      memory: sandboxMemory,
      isSimulation: true,
    });

    const simulationResults = {
      planId: plan.id,
      startTime: Date.now(),
      steps: [],
      riskAssessment: {},
      criticalIssues: [],
    };

    try {
      // Execute each step in simulation mode
      for (const step of plan.steps) {
        const stepResult = await sandboxOrchestrator.executeStep(step, {
          simulationMode: true,
          recordArtifacts: true,
        });

        simulationResults.steps.push({
          stepId: step.id,
          success: stepResult.success,
          uncertaintyScore: stepResult.uncertaintyScore,
          potentialIssues: stepResult.potentialIssues,
        });

        // Detect critical issues that would block execution
        if (stepResult.riskScore > this.riskThresholds.high) {
          simulationResults.criticalIssues.push({
            step: step.id,
            riskScore: stepResult.riskScore,
            description: stepResult.riskDescription,
          });
        }
      }

      // Analyze overall simulation results
      simulationResults.riskAssessment = this._assessOverallRisk(
        simulationResults.steps
      );
      simulationResults.endTime = Date.now();

      return simulationResults;
    } catch (error) {
      this.logger.error(`Simulation failed: ${error.message}`);
      simulationResults.failed = true;
      simulationResults.error = error.message;
      return simulationResults;
    } finally {
      // Clean up simulation resources
      await sandboxMemory.clear();
    }
  }

  /**
   * Assess overall risk based on individual step results
   * @private
   */
  _assessOverallRisk(stepResults) {
    // Analyze simulation results to produce overall risk assessment
    const uncertaintyScores = stepResults.map((r) => r.uncertaintyScore);
    const avgUncertainty =
      uncertaintyScores.reduce((sum, score) => sum + score, 0) /
      stepResults.length;
    const maxUncertainty = Math.max(...uncertaintyScores);
    const issueCount = stepResults.reduce(
      (count, step) => count + step.potentialIssues.length,
      0
    );

    // Calculate composite risk score
    const compositeRiskScore =
      avgUncertainty * 0.4 +
      maxUncertainty * 0.4 +
      Math.min(issueCount / 10, 1) * 0.2;

    return {
      compositeRiskScore,
      riskLevel: this._determineRiskLevel(compositeRiskScore),
      recommendedActions: this._generateRecommendations(
        compositeRiskScore,
        stepResults
      ),
    };
  }

  /**
   * Determine risk level based on composite score
   * @private
   */
  _determineRiskLevel(score) {
    if (score >= this.riskThresholds.high) return "HIGH";
    if (score >= this.riskThresholds.medium) return "MEDIUM";
    if (score >= this.riskThresholds.low) return "LOW";
    return "MINIMAL";
  }

  /**
   * Generate recommendations based on risk assessment
   * @private
   */
  _generateRecommendations(riskScore, stepResults) {
    const recommendations = [];

    if (riskScore >= this.riskThresholds.high) {
      recommendations.push("Require explicit human approval before execution");
      recommendations.push(
        "Consider splitting plan into smaller, safer sub-plans"
      );
    }

    if (riskScore >= this.riskThresholds.medium) {
      recommendations.push("Implement additional validation steps");
      recommendations.push("Add explicit rollback procedures for each step");
    }

    // Analyze specific step issues
    stepResults.forEach((step) => {
      if (step.potentialIssues.length > 0) {
        recommendations.push(
          `Address issues in step ${step.stepId} before execution`
        );
      }
    });

    return recommendations;
  }
}

module.exports = { SimulationTester };
