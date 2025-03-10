const express = require("express");
const { invokeAiderCodex } = require("../controllers/invokeAiderCodex");
const router = express.Router();

/**
 * @route POST /api/aider-codex/analyze
 * @desc Analyze code using Aider Codex
 * @access Public
 */
router.post("/analyze", async (req, res) => {
  try {
    const { code, options } = req.body;
    
    if (!code) {
      return res.status(400).json({ error: "Code input is required" });
    }
    
    const result = await invokeAiderCodex(code, options);
    return res.json(result);
  } catch (error) {
    console.error("Error in Aider Codex route:", error);
    return res.status(500).json({ error: "Failed to analyze code" });
  }
});

/**
 * @route GET /api/aider-codex/status
 * @desc Check Aider Codex service status
 * @access Public
 */
router.get("/status", (req, res) => {
  res.json({ status: "operational" });
});

module.exports = router;