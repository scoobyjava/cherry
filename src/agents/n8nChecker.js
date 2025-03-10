const { exec } = require("child_process");
const logger = require("../utils/unifiedLogger");

function checkN8n() {
  exec("pgrep -f n8n", (error, stdout, stderr) => {
    if (error || !stdout.trim()) {
      logger.error("n8n process not detected. Attempting restart...", {
        error: error && error.message,
      });
      exec(
        process.env.N8N_START_CMD || "docker start n8n_container",
        (restartErr) => {
          if (restartErr) {
            logger.error("Failed to restart n8n: " + restartErr.message, {
              error: restartErr,
            });
          } else {
            logger.info("n8n restarted successfully.");
          }
        }
      );
    } else {
      logger.info("n8n is running fine.");
    }
  });
}

// Agent real-time communication hub
class AgentCommunicationHub {
  constructor(server) {
    this.io = require("socket.io")(server);
    this.connections = new Map();
    this.messageHandlers = new Map();
    this.setupConnectionHandlers();
  }

  setupConnectionHandlers() {
    this.io.on("connection", (socket) => {
      // Authenticate the connection
      socket.on("register", (data, callback) => {
        if (this.authenticateAgent(data)) {
          this.connections.set(data.agentId, {
            socket,
            info: {
              name: data.agentName,
              capabilities: data.capabilities,
              status: "connected",
            },
          });
          logger.info(`Agent connected: ${data.agentName}`);
          callback({ success: true });

          // Notify others
          this.broadcast("agent:connected", {
            agentId: data.agentId,
            name: data.agentName,
          });
        } else {
          callback({ success: false, error: "Authentication failed" });
          socket.disconnect();
        }
      });

      // Handle agent messages
      socket.on("message", (message) => {
        this.handleAgentMessage(socket, message);
      });

      // Handle disconnection
      socket.on("disconnect", () => {
        let disconnectedAgentId = null;
        for (const [agentId, conn] of this.connections.entries()) {
          if (conn.socket === socket) {
            disconnectedAgentId = agentId;
            break;
          }
        }

        if (disconnectedAgentId) {
          const agentInfo = this.connections.get(disconnectedAgentId).info;
          logger.info(`Agent disconnected: ${agentInfo.name}`);
          this.connections.delete(disconnectedAgentId);

          // Notify others
          this.broadcast("agent:disconnected", {
            agentId: disconnectedAgentId,
            name: agentInfo.name,
          });
        }
      });
    });
  }

  authenticateAgent(data) {
    // You would implement proper authentication here
    return data && data.agentId && data.agentName;
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

    // Send to target agent if specified
    if (message.targetAgentId) {
      const targetConn = this.connections.get(message.targetAgentId);
      if (targetConn) {
        targetConn.socket.emit("message", {
          type: message.type,
          data: message.data,
          from: senderAgentId,
        });
      }
    }

    // Or broadcast if it's a broadcast message
    if (message.broadcast) {
      this.broadcast(message.type, message.data, senderAgentId);
    }
  }

  broadcast(type, data, excludeAgentId = null) {
    this.connections.forEach((conn, agentId) => {
      if (agentId !== excludeAgentId) {
        conn.socket.emit("message", { type, data });
      }
    });
  }

  registerMessageHandler(type, handler) {
    this.messageHandlers.set(type, handler);
    return this;
  }

  getConnectedAgents() {
    return Array.from(this.connections.entries()).map(([agentId, conn]) => ({
      id: agentId,
      ...conn.info,
    }));
  }
}

module.exports = { checkN8n, AgentCommunicationHub };
