import { SystemMetrics, OptimizationResult } from "./types";
import { MetricsCollector } from "../metrics/metricsCollector";
import { SwarmController } from "../agents/swarmController";

export class SelfOptimizer {
  private metricsCollector: MetricsCollector;
  private swarmController: SwarmController;

  private readonly OPTIMIZATION_TRIGGERS = {
    PERF_THRESHOLD: 0.85, // Kick in when system load exceeds 85%
    TACTICS: {
      RAMJET: (metrics: SystemMetrics) =>
        metrics.taskQueue > 100 ? { parallelization: 3.0 } : null,
      SCORCHED_EARTH: (metrics: SystemMetrics) =>
        metrics.errorRate > 0.3 ? { killswitch: "ERROR_PRONE_AGENTS" } : null,
      RESOURCE_BURST: (metrics: SystemMetrics) =>
        metrics.responseTime > 2000 ? { resourceAllocation: "BURST" } : null,
    },
  };

  constructor(
    metricsCollector: MetricsCollector,
    swarmController: SwarmController
  ) {
    this.metricsCollector = metricsCollector;
    this.swarmController = swarmController;
  }

  async runOptimizationCycle(): Promise<OptimizationResult> {
    // Collect current system metrics
    const metrics = await this.metricsCollector.collectMetrics();

    // Check if optimization is needed
    if (this.shouldOptimize(metrics)) {
      return this.optimizeBattlefield(metrics);
    }

    return { optimized: false, reason: "No optimization needed" };
  }

  private shouldOptimize(metrics: SystemMetrics): boolean {
    return metrics.systemLoad > this.OPTIMIZATION_TRIGGERS.PERF_THRESHOLD;
  }

  private optimizeBattlefield(metrics: SystemMetrics): OptimizationResult {
    // Evaluate which tactic to use based on current metrics
    for (const [tactic, evaluator] of Object.entries(
      this.OPTIMIZATION_TRIGGERS.TACTICS
    )) {
      const params = evaluator(metrics);
      if (params) {
        // Execute the selected tactic via the swarm controller
        this.swarmController.executeTactic(tactic, params);
        return {
          optimized: true,
          tactic,
          params,
          reason: `Applied ${tactic} due to metrics: ${JSON.stringify(params)}`,
        };
      }
    }
    // If no specific tactic matched, perform a general/fallback optimization
    return this.performGeneralOptimization(metrics);
  }

  private performGeneralOptimization(
    metrics: SystemMetrics
  ): OptimizationResult {
    if (metrics.memoryUsage > 0.9) {
      this.swarmController.releaseMemoryBuffers();
      return {
        optimized: true,
        tactic: "GENERAL_MEMORY_RELEASE",
        params: null,
        reason: "Released memory buffers due to high memory usage",
      };
    } else if (metrics.cpuLoad > 0.8) {
      this.swarmController.deferNonCriticalTasks();
      return {
        optimized: true,
        tactic: "GENERAL_CPU_SLOWDOWN",
        params: null,
        reason: "Deferred non-critical tasks due to high CPU load",
      };
    }
    return { optimized: false, reason: "No general optimization applicable" };
  }
}
