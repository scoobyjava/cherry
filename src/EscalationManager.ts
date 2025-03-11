import { SystemMetrics, OptimizationImpact } from "./optimization";

interface EscalationCriteria {
  errorRateThreshold: number;
  systemLoadThreshold: number;
  recoveryTimeThresholdMs: number;
  memoryGrowthThresholdMb?: number;
  consecutiveFailuresThreshold?: number;
}

interface EscalationMessage {
  urgency: "low" | "medium" | "high";
  message: string;
  timestamp: number;
  context?: Record<string, any>;
  suggestedActions?: string[];
}

interface EscalationHistory {
  recentEscalations: Map<string, EscalationRecord[]>;
  thresholdAdjustments: Map<string, number>;
}

interface EscalationRecord {
  timestamp: number;
  metric: string;
  value: number;
  threshold: number;
  resolved: boolean;
  resolutionTime?: number;
}

// Main EscalationManager class with enhanced memory management and adaptive thresholds
export class EscalationManager {
  private criteria: EscalationCriteria;
  private sendNotification: (msg: EscalationMessage) => void;
  private history: EscalationHistory;
  private readonly MAX_HISTORY_SIZE = 100;
  private readonly LEARNING_RATE = 0.05;
  private readonly MEMORY_CHECK_INTERVAL = 60000; // 1 minute
  private readonly ANOMALY_DETECTION_WINDOW = 10;
  private lastMemoryUsage: number = process.memoryUsage().heapUsed;
  private memoryCheckTimer: NodeJS.Timeout | null = null;

  constructor(
    criteria: EscalationCriteria,
    sendNotification: (msg: EscalationMessage) => void
  ) {
    this.criteria = {
      ...criteria,
      // Default values if not provided
      memoryGrowthThresholdMb: criteria.memoryGrowthThresholdMb || 100,
      consecutiveFailuresThreshold: criteria.consecutiveFailuresThreshold || 3,
    };
    this.sendNotification = sendNotification;
    this.history = {
      recentEscalations: new Map(),
      thresholdAdjustments: new Map(),
    };

    // Start memory monitoring
    this.startMemoryMonitoring();
  }

  // Enhanced evaluation with anomaly detection and adaptive thresholds
  evaluate(metrics: SystemMetrics, impact?: OptimizationImpact): void {
    // Check for anomalies using historical data
    const anomalies = this.detectAnomalies(metrics);
    if (anomalies.length > 0) {
      this.escalate(
        "medium",
        `Detected anomalies in: ${anomalies.join(", ")}`,
        { anomalies }
      );
    }

    // Enhanced error rate check with adaptive threshold
    const adjustedErrorThreshold = this.getAdjustedThreshold("errorRate");
    if ((metrics.errorRate || 0) > adjustedErrorThreshold) {
      const consecutive = this.checkConsecutiveIssues("errorRate");
      const urgency =
        consecutive >= (this.criteria.consecutiveFailuresThreshold || 3)
          ? "high"
          : "medium";

      this.escalate(
        urgency,
        this.generateNaturalMessage(
          "errorRate",
          metrics.errorRate,
          adjustedErrorThreshold,
          consecutive
        ),
        {
          metric: "errorRate",
          value: metrics.errorRate,
          threshold: adjustedErrorThreshold,
          consecutive,
        },
        consecutive > 1
          ? ["Review error logs", "Check recent deployments", "Scale resources"]
          : undefined
      );
      this.recordEscalation(
        "errorRate",
        metrics.errorRate || 0,
        adjustedErrorThreshold
      );
    }

    // System load check with adaptive threshold
    const adjustedLoadThreshold = this.getAdjustedThreshold("systemLoad");
    if ((metrics.systemLoad || 0) > adjustedLoadThreshold) {
      const consecutive = this.checkConsecutiveIssues("systemLoad");
      this.escalate(
        consecutive > 1 ? "high" : "medium",
        this.generateNaturalMessage(
          "systemLoad",
          metrics.systemLoad,
          adjustedLoadThreshold,
          consecutive
        ),
        {
          metric: "systemLoad",
          value: metrics.systemLoad,
          threshold: adjustedLoadThreshold,
          consecutive,
        },
        ["Scale out resources", "Check for resource-intensive tasks"]
      );
      this.recordEscalation(
        "systemLoad",
        metrics.systemLoad || 0,
        adjustedLoadThreshold
      );
    }

    // Response time check from impact data
    if (
      impact &&
      impact.responseTimeDelta > this.criteria.recoveryTimeThresholdMs
    ) {
      const consecutive = this.checkConsecutiveIssues("responseTime");
      this.escalate(
        "medium",
        this.generateNaturalMessage(
          "responseTime",
          impact.responseTimeDelta,
          this.criteria.recoveryTimeThresholdMs,
          consecutive
        ),
        {
          metric: "responseTime",
          value: impact.responseTimeDelta,
          threshold: this.criteria.recoveryTimeThresholdMs,
          consecutive,
        },
        ["Review optimization strategies", "Check for network latency"]
      );
      this.recordEscalation(
        "responseTime",
        impact.responseTimeDelta,
        this.criteria.recoveryTimeThresholdMs
      );
    }

    // Clean up old history entries
    this.pruneHistory();
  }

  // Mark an escalation as resolved
  resolveEscalation(metric: string, timestamp: number): void {
    const records = this.history.recentEscalations.get(metric);
    if (records) {
      const record = records.find(
        (r) => r.timestamp === timestamp && !r.resolved
      );
      if (record) {
        record.resolved = true;
        record.resolutionTime = Date.now() - timestamp;

        // Adjust threshold based on resolution
        this.adjustThreshold(metric, record.value);
      }
    }
  }

  // Stop monitoring and clean up
  destroy(): void {
    if (this.memoryCheckTimer) {
      clearInterval(this.memoryCheckTimer);
      this.memoryCheckTimer = null;
    }
  }

  // Private methods
  private escalate(
    urgency: "low" | "medium" | "high",
    detail: string,
    context?: Record<string, any>,
    suggestedActions?: string[]
  ): void {
    const message: EscalationMessage = {
      urgency,
      message: detail,
      timestamp: Date.now(),
      context,
      suggestedActions,
    };
    this.sendNotification(message);
  }

  private startMemoryMonitoring(): void {
    this.memoryCheckTimer = setInterval(() => {
      const currentMemory = process.memoryUsage().heapUsed;
      const memoryGrowthMb =
        (currentMemory - this.lastMemoryUsage) / (1024 * 1024);

      if (memoryGrowthMb > (this.criteria.memoryGrowthThresholdMb || 100)) {
        this.escalate(
          "high",
          `Memory usage has grown by ${memoryGrowthMb.toFixed(
            2
          )}MB in the last minute. Possible memory leak.`,
          { memoryGrowthMb, currentMemoryMb: currentMemory / (1024 * 1024) },
          [
            "Check for memory leaks",
            "Review recent code changes",
            "Consider restarting the service",
          ]
        );
      }

      this.lastMemoryUsage = currentMemory;
    }, this.MEMORY_CHECK_INTERVAL);
  }

  private recordEscalation(
    metric: string,
    value: number,
    threshold: number
  ): void {
    if (!this.history.recentEscalations.has(metric)) {
      this.history.recentEscalations.set(metric, []);
    }

    const records = this.history.recentEscalations.get(metric)!;
    records.push({
      timestamp: Date.now(),
      metric,
      value,
      threshold,
      resolved: false,
    });
  }

  private pruneHistory(): void {
    const now = Date.now();
    for (const [metric, records] of this.history.recentEscalations.entries()) {
      // Keep only recent records and those that are unresolved
      const prunedRecords = records.filter(
        (record) =>
          !record.resolved || now - record.timestamp < 24 * 60 * 60 * 1000 // 24 hours
      );

      // Keep the most recent MAX_HISTORY_SIZE records
      if (prunedRecords.length > this.MAX_HISTORY_SIZE) {
        prunedRecords.splice(0, prunedRecords.length - this.MAX_HISTORY_SIZE);
      }

      this.history.recentEscalations.set(metric, prunedRecords);
    }
  }

  private checkConsecutiveIssues(metric: string): number {
    const records = this.history.recentEscalations.get(metric);
    if (!records || records.length === 0) return 0;

    let count = 0;
    const last5Minutes = Date.now() - 5 * 60 * 1000;

    // Count recent unresolved issues
    for (let i = records.length - 1; i >= 0; i--) {
      if (records[i].timestamp > last5Minutes && !records[i].resolved) {
        count++;
      } else {
        break;
      }
    }

    return count;
  }

  private getAdjustedThreshold(metric: string): number {
    const baseThreshold = this.getBaseThreshold(metric);
    const adjustment = this.history.thresholdAdjustments.get(metric) || 1.0;
    return baseThreshold * adjustment;
  }

  private getBaseThreshold(metric: string): number {
    switch (metric) {
      case "errorRate":
        return this.criteria.errorRateThreshold;
      case "systemLoad":
        return this.criteria.systemLoadThreshold;
      case "responseTime":
        return this.criteria.recoveryTimeThresholdMs;
      default:
        return 0;
    }
  }

  private adjustThreshold(metric: string, value: number): void {
    const baseThreshold = this.getBaseThreshold(metric);
    if (baseThreshold === 0) return;

    const currentAdjustment =
      this.history.thresholdAdjustments.get(metric) || 1.0;

    // If the value is much higher than threshold, consider adjusting up
    // This helps prevent constant alerts for temporary spikes
    if (value > baseThreshold * 1.5) {
      const newAdjustment = currentAdjustment * (1 + this.LEARNING_RATE);
      this.history.thresholdAdjustments.set(
        metric,
        Math.min(newAdjustment, 1.5)
      ); // Cap at 50% increase
    }
    // If value is near threshold, consider adjusting down
    // This helps maintain sensitivity to real issues
    else if (value < baseThreshold * 0.7 && currentAdjustment > 1.0) {
      const newAdjustment = currentAdjustment * (1 - this.LEARNING_RATE);
      this.history.thresholdAdjustments.set(
        metric,
        Math.max(newAdjustment, 1.0)
      ); // Don't go below base
    }
  }

  private detectAnomalies(metrics: SystemMetrics): string[] {
    const anomalies: string[] = [];

    // Simple anomaly detection using Z-score with recent history
    for (const [metric, records] of this.history.recentEscalations.entries()) {
      if (records.length < this.ANOMALY_DETECTION_WINDOW) continue;

      // Get recent values
      const recentValues = records
        .slice(-this.ANOMALY_DETECTION_WINDOW)
        .map((r) => r.value);

      // Calculate mean and standard deviation
      const mean =
        recentValues.reduce((sum, val) => sum + val, 0) / recentValues.length;
      const stdDev = Math.sqrt(
        recentValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) /
          recentValues.length
      );

      // Get current value for this metric
      let currentValue: number | undefined;
      switch (metric) {
        case "errorRate":
          currentValue = metrics.errorRate;
          break;
        case "systemLoad":
          currentValue = metrics.systemLoad;
          break;
        // Add other metrics as needed
      }

      // Check if current value is an anomaly (Z-score > 3)
      if (currentValue !== undefined && stdDev > 0) {
        const zScore = Math.abs((currentValue - mean) / stdDev);
        if (zScore > 3) {
          anomalies.push(`${metric} (z-score: ${zScore.toFixed(2)})`);
        }
      }
    }

    return anomalies;
  }

  private generateNaturalMessage(
    metric: string,
    value: number,
    threshold: number,
    consecutive: number
  ): string {
    // Format value and threshold based on metric type
    let formattedValue: string;
    let formattedThreshold: string;
    let unit: string;

    switch (metric) {
      case "errorRate":
        formattedValue = `${(value * 100).toFixed(1)}%`;
        formattedThreshold = `${(threshold * 100).toFixed(1)}%`;
        unit = "error rate";
        break;
      case "systemLoad":
        formattedValue = `${(value * 100).toFixed(1)}%`;
        formattedThreshold = `${(threshold * 100).toFixed(1)}%`;
        unit = "system load";
        break;
      case "responseTime":
        formattedValue = `${value.toFixed(0)}ms`;
        formattedThreshold = `${threshold.toFixed(0)}ms`;
        unit = "response time";
        break;
      default:
        formattedValue = value.toString();
        formattedThreshold = threshold.toString();
        unit = metric;
    }

    // Create a more natural message based on consecutive occurrences
    if (consecutive <= 1) {
      return `I've detected that the ${unit} is ${formattedValue}, which exceeds our threshold of ${formattedThreshold}. Would you like me to investigate?`;
    } else if (consecutive <= 3) {
      return `This is concerning - the ${unit} has been at ${formattedValue} for ${consecutive} consecutive checks (threshold: ${formattedThreshold}). Should I try an automatic remediation?`;
    } else {
      return `URGENT: The ${unit} has remained elevated at ${formattedValue} for ${consecutive} consecutive checks, well above our threshold of ${formattedThreshold}. This requires immediate attention!`;
    }
  }

  /**
   * Returns memory diagnostics with current usage and growth trends.
   * This helps with external monitoring integration.
   */
  getMemoryDiagnostics(): {
    current: NodeJS.MemoryUsage;
    trends: { growthRateMbPerHour: number };
  } {
    const current = process.memoryUsage();

    // Calculate hourly growth rate based on data we already track
    const hourlyGrowthRate = this.calculateMemoryGrowthRate();

    return {
      current,
      trends: {
        growthRateMbPerHour: hourlyGrowthRate,
      },
    };
  }

  /**
   * Calculate memory growth rate based on stored measurements.
   * @returns Growth rate in MB per hour
   */
  private calculateMemoryGrowthRate(): number {
    // For now, use a simple calculation based on our last memory check
    // In a more advanced version, you might store multiple snapshots for better trending
    const currentMemory = process.memoryUsage().heapUsed;
    const memoryDeltaBytes = currentMemory - this.lastMemoryUsage;
    const memoryDeltaMb = memoryDeltaBytes / (1024 * 1024);

    // Convert from MB per MEMORY_CHECK_INTERVAL to MB per hour
    const hoursPerInterval = this.MEMORY_CHECK_INTERVAL / (1000 * 60 * 60);
    return memoryDeltaMb / hoursPerInterval;
  }

  /**
   * Integration method for external hybrid storage.
   * Can be used to offload historical data to persistent storage.
   * @param persistentStorage The storage provider (e.g., Redis)
   */
  setupPersistentStorageBackup(persistentStorage: {
    save: (key: string, data: any) => Promise<void>;
  }): void {
    // Setup periodic backup of escalation history
    setInterval(async () => {
      // For each metric, store its history
      for (const [
        metric,
        records,
      ] of this.history.recentEscalations.entries()) {
        if (records.length > 0) {
          await persistentStorage.save(`cherry:escalation:${metric}`, records);
        }
      }

      // Also backup threshold adjustments
      await persistentStorage.save(
        "cherry:thresholds",
        Object.fromEntries(this.history.thresholdAdjustments)
      );
    }, 300000); // Every 5 minutes
  }
}

// Example usage:
/*
const escalationManager = new EscalationManager({
  errorRateThreshold: 0.05,
  systemLoadThreshold: 0.8,
  recoveryTimeThresholdMs: 200,
  memoryGrowthThresholdMb: 100,
  consecutiveFailuresThreshold: 3
}, (message) => {
  // Handle notification (e.g., send to Slack, email, dashboard)
  console.log(`[${message.urgency.toUpperCase()}] ${message.message}`);
  if (message.suggestedActions) {
    console.log(`Suggested actions: ${message.suggestedActions.join(', ')}`);
  }
});

// Example periodic evaluation
setInterval(() => {
  const metrics = getCurrentMetrics(); // Your function to get metrics
  const impact = getOptimizationImpact(); // Your function to get impact
  escalationManager.evaluate(metrics, impact);
}, 60000); // Check every minute
*/
