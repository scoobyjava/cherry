const express = require('express');
const http = require('http');
const cors = require('cors');
const dotenv = require('dotenv');
const OrchestratorBridge = require('../agent_system/orchestrator_bridge');

// Load environment variables
dotenv.config();

// Initialize express app
const app = express();
const server = http.createServer(app);

// Middleware
app.use(cors());
app.use(express.json());

// Initialize orchestrator bridge
const orchestratorBridge = new OrchestratorBridge();
orchestratorBridge.setupWebSocketServer(server);
orchestratorBridge.startPythonOrchestrator();

// Define routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Cherry Website API is running' });
});

// Add user routes
const userRoutes = require('./api/user_routes');
app.use('/api/users', userRoutes);

// Fallback route
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = server;
