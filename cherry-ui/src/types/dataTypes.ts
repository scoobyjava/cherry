export interface AgentStatus {
  id: string;
  status: 'active' | 'inactive' | 'error';
  lastUpdated: string; // ISO string
  message: string;
}

export interface ConversationMessage {
  id: string;
  sender: string;
  message: string;
  timestamp: string; // ISO string
}

export interface PerformanceData {
  cpuUsage: number;      // Percentage
  memoryUsage: number;   // MB
  diskUsage?: number;    // MB, optional
  timestamp: string;     // ISO string
}
