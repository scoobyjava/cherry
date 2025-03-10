const express = require('express');
const logger = require('../utils/unifiedLogger');
const cherryAPI = require('./cherryAPI');
const app = express();
const PORT = process.env.WEBHOOK_PORT || 3001;

// Parse JSON payloads (no need for external body-parser)
app.use(express.json());

// Mount API endpoints for Cherry Command Center
app.use('/api/cherry', cherryAPI);

// GitHub webhook endpoint
app.post('/webhook/github', async (req, res) => {
  const event = req.header('X-GitHub-Event');
  const payload = req.body;
  logger.info('Received GitHub webhook event', { event, repository: payload.repository?.full_name });
  // Process events as needed (e.g. triggering memory updates, code analysis, etc.)
  res.status(200).send('Webhook received');
});

app.listen(PORT, () => {
  logger.info(`GitHub Webhook endpoint / Cherry API listening on port ${PORT}`);
});