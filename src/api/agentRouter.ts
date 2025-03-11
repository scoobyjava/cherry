import express from 'express';
import { debateAndDecide, codeAnalysisProposal } from '../agents/swarmManager';
import { StrategyRegistry } from '../optimization';

const router = express.Router();

// Get all available agents
router.get('/agents', (req, res) => {
  const agents = {
    'cherry': { name: 'Cherry', role: 'Orchestrator', status: 'active' },
    'code-analyzer': { name: 'Code Analyzer', role: 'Development', status: 'active' },
    'memory-curator': { name: 'Memory Curator', role: 'Knowledge Management', status: 'active' },
    'command-interface': { name: 'Command Interface', role: 'User Interaction', status: 'active' },
    'visual-design': { name: 'Visual Design', role: 'UI/UX', status: 'active' }
  };
  
  res.json({ agents });
});

// Agent message endpoint
router.post('/agent/:agentId/message', async (req, res) => {
  try {
    const { agentId } = req.params;
    const { content, senderId, metadata } = req.body;
    
    // Use the existing swarmManager functionality
    const proposal = await debateAndDecide(content);
    
    res.json({
      response: proposal.proposal,
      confidence: proposal.score,
      agent: proposal.agent,
      context: metadata
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create group chat with multiple agents
router.post('/swarm', async (req, res) => {
  try {
    const { agents, topic, initiator } = req.body;
    
    // Create a swarm session ID
    const swarmId = `swarm-${Date.now()}`;
    
    res.json({
      swarmId,
      agents,
      status: 'initiated',
      message: `Swarm created with agents: ${agents.join(', ')}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
