const express = require("express");
const path = require("path");
const http = require("http");
const socketIo = require("socket.io");
const { debugRouter, setupErrorHandlers } = require("./utils/debugTeam");
const { ConfigLoader } = require("./config/config_loader");
const agentRouter = require("./api/agentRouter");

const app = express();
const server = http.createServer(app);
const io = socketIo(server);
const PORT = process.env.PORT || 3000;

// Setup middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "public")));

// Set up API routes
app.use("/api/debug", debugRouter);
app.use("/api/cherry", agentRouter);

// Dashboard route
app.get("/dashboard", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "dashboard.html"));
});

// Setup WebSocket for real-time agent communication
io.on("connection", (socket) => {
  console.log("New client connected");
  
  socket.on("join-agent-channel", (agentId) => {
    socket.join(`agent-${agentId}`);
  });
  
  socket.on("join-swarm", (swarmId) => {
    socket.join(`swarm-${swarmId}`);
  });
  
  socket.on("disconnect", () => {
    console.log("Client disconnected");
  });
});

// Set up error handlers
setupErrorHandlers();

// Initialize configuration
async function initializeApp() {
  try {
    // Load configuration
    const config = await ConfigLoader.loadConfig(
      path.join(__dirname, "../config/app_config.json")
    );

    // Start server
    server.listen(PORT, () => {
      console.log(`Cherry server running on port ${PORT}`);
    });
  } catch (error) {
    console.error("Failed to initialize app:", error);
    process.exit(1);
  }
}

// Initialize the application
initializeApp().catch(console.error);

module.exports = { app, server, io };