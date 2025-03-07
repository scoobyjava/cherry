const express = require('express');
const http = require('http');
const path = require('path');
const socketIo = require('socket.io');
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Serve static assets from the "public" directory.
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// REST endpoint to chat with a specific agent.
// The request body should contain:
//   { "agent": "cherry" or specific agent name, "message": "user message" }
app.post('/api/chat', (req, res) => {
  const agent = req.body.agent || 'cherry';
  const userMessage = req.body.message;

  // For example, we assume a Python agent is invoked which outputs the response.
  // You can later enhance this to use a proper API or integrate multiple agents.
  // We'll pass the agent name and the message as command line arguments.
  const agentProcess = spawn('python3', [`../src/agents/${agent}_agent.py`, userMessage]);

  let responseData = '';
  agentProcess.stdout.on('data', (data) => {
    responseData += data.toString();
  });
  agentProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
  agentProcess.on('close', (code) => {
    res.json({ response: responseData });
  });
});

// Socket.io for real-time multi-user/group chat.
io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('chat message', (msgObj) => {
    // msgObj should be { agent: "cherry" (or other), message: "<user message>" }
    const agent = msgObj.agent || 'cherry';
    const message = msgObj.message;

    // For simplicity, also call the respective Python agent.
    const agentProcess = spawn('python3', [`../src/agents/${agent}_agent.py`, message]);
    let response = '';
    agentProcess.stdout.on('data', (data) => {
      response += data.toString();
    });
    agentProcess.on('close', () => {
      // Emit the response along with user message to all connected clients.
      io.emit('chat message', { agent, user: message, response });
    });
  });

  socket.on('disconnect', () => {
    console.log('user disconnected');
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});