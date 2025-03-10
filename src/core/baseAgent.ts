abstract class BaseAgent implements Agent {
  id: string;
  name: string;
  capabilities: string[];
  priority: number = 5; // Default priority (1-10)
  
  constructor(config: AgentConfig) {
    this.id = config.id;
    this.name = config.name;
    this.capabilities = config.capabilities;
    this.priority = config.priority || 5;
  }
  
  // Core execution method all agents must implement
  abstract execute(task: Task): Promise<AgentResult>;
  
  // New methods for 2.0
  async preempt(higherPriorityTask: Task): Promise<boolean> {
    // Default implementation - can be overridden
    return this.priority < higherPriorityTask.priority;
  }
  
  getStatus(): AgentStatus {
    return {
      id: this.id,
      status: "ready",
      currentLoad: this._getCurrentLoad(),
      avgResponseTime: this._calculateAvgResponseTime()
    };
  }
  
  protected _getCurrentLoad(): number {
    // Implementation to report current load
    return 0; 
  }
  
  protected _calculateAvgResponseTime(): number {
    // Implementation to calculate average response time
    return 0;
  }
}
