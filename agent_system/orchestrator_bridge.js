const WebSocket = require('ws');
const { spawn } = require('child_process');
const logger = require('../utils/logger');

class OrchestratorBridge {
  constructor() {
    this.connections = new Map();
    this.messageHandlers = new Map();
    this.pythonProcess = null;
  }

  startPythonOrchestrator() {
    logger.info('Starting Python orchestrator...');
    this.pythonProcess = spawn('python', ['orchestration/code_generator.py']);
    
    this.pythonProcess.stdout.on('data', (data) => {
      logger.info(`Orchestrator: ${data}`);
    });
    
    this.pythonProcess.stderr.on('data', (data) => {
      logger.error(`Orchestrator error: ${data}`);
    });
    
    this.pythonProcess.on('close', (code) => {
      logger.info(`Orchestrator process exited with code ${code}`);
    });
  }

  setupWebSocketServer(server) {
    const wss = new WebSocket.Server({ server });
    
    wss.on('connection', (ws) => {
      const agentId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
      
      this.connections.set(agentId, {
        socket: ws,
        info: {
          name: 'Agent-' + agentId,
          capabilities: [],
          status: 'connected'
        }
      });
      
      ws.on('message', (message) => {
        try {
          const parsedMessage = JSON.parse(message);
          this.handleAgentMessage(ws, parsedMessage);
        } catch (error) {
          logger.error('Error parsing message:', error);
        }
      });
      
      ws.on('close', () => {
        let disconnectedAgentId = null;
        for (const [id, conn] of this.connections.entries()) {
          if (conn.socket === ws) {
            disconnectedAgentId = id;
            break;
          }
        }
        
        if (disconnectedAgentId) {
          const agentInfo = this.connections.get(disconnectedAgentId).info;
          logger.info(`Agent disconnected: ${agentInfo.name}`);
          this.connections.delete(disconnectedAgentId);
          this.broadcast('agent:disconnected', {
            agentId: disconnectedAgentId,
            name: agentInfo.name
          });
        }
      });
    });
  }
  
  handleAgentMessage(socket, message) {
    if (!message || !message.type) return;
    
    // Find the sender
    let senderAgentId = null;
    for (const [agentId, conn] of this.connections.entries()) {
      if (conn.socket === socket) {
        senderAgentId = agentId;
        break;
      }
    }
    
    if (!senderAgentId) return;
    
    // Handle message
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(senderAgentId, message.data);
    }
    
    // Forward task requests to the Python orchestrator
    if (message.type === 'task:request') {
      this.forwardTaskToPython(message.data);
    }
    
    // Send to target agent if specified
    if (message.targetAgentId) {
      const targetConn = this.connections.get(message.targetAgentId);
      if (targetConn) {
        targetConn.socket.send(JSON.stringify({
          type: message.type,
          data: message.data,
          from: senderAgentId
        }));
      }
    // Or broadcast if it's a broadcast message
    } else if (message.broadcast) {
      this.broadcast(message.type, message.data, senderAgentId);
    }
  }
  
  forwardTaskToPython(taskData) {
    // In a real implementation, this would use inter-process communication
    // For now, we'll write to a file that the Python process can watch
    const fs = require('fs');
    const taskFile = 'orchestration/tasks/' + Date.now() + '.json';
    
    fs.mkdirSync('orchestration/tasks', { recursive: true });
    fs.writeFileSync(taskFile, JSON.stringify(taskData));
    
    logger.info(`Task forwarded to Python orchestrator: ${taskFile}`);
  }
  
  broadcast(type, data, excludeAgentId = null) {
    const message = JSON.stringify({ type, data });
    
    for (const [agentId, conn] of this.connections.entries()) {
      if (excludeAgentId && agentId === excludeAgentId) continue;
      conn.socket.send(message);
    }
  }
  
  registerMessageHandler(type, handler) {
    this.messageHandlers.set(type, handler);
    return this;
  }
  
  getConnectedAgents() {
    return Array.from(this.connections.entries())
      .map(([agentId, conn]) => ({
        id: agentId,
        ...conn.info
      }));
  }
}

module.exports = OrchestratorBridge;
