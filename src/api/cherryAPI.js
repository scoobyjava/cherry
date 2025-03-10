const express = require('express');
const router = express.Router();
const { generateLogo } = require('../agents/visualDesignAgent');
const { classifyCommand } = require('../agents/commandInterface');
const { runCodeAnalysis } = require('../agents/codeAnalyzer');
const fs = require('fs');
const path = require('path');

// Endpoint to generate and return logo data.
router.get('/logo', async (req, res) => {
  try {
    const logoData = await generateLogo();
    res.json({ logoData });
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
});

// Endpoint to classify a command.
router.post('/classify', async (req, res) => {
  try {
    const { command } = req.body;
    const result = await classifyCommand(command);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
});

// Endpoint to trigger code analysis.
router.get('/code-analysis', async (req, res) => {
  try {
    runCodeAnalysis();
    res.json({ status: "Code analysis initiated. Check logs for output." });
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
});

// Endpoint to get memory summary.
router.get('/memory-summary', (req, res) => {
  try {
    const summary = fs.readFileSync(path.join(__dirname, '../logs/memorySummary.log'), 'utf8');
    res.json({ summary });
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
});

module.exports = router;