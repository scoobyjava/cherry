const enhancedAgentConfig = {
  name: "Cherry Network Agent",
  instructions: `
    - Coordinate with AgentOrchestrator for distributed tasks
    - Utilize socket-based communication for real-time updates
    - Leverage existing debug team capabilities
    - Implement file search and organization across distributed storage
    - Route requests to specialized agents based on task requirements
    - Process content using advanced language models
    - Monitor and validate operations through custom guardrails
  `,
  tools: [
    fileSearch, 
    webSearch, 
    socketCommunication,
    cherryStorageAccess,
    triageRouter,
    contentProcessor
  ]
};
