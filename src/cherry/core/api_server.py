from fastapi import FastAPI
from agent_orchestrator import AgentOrchestrator

app = FastAPI()
orchestrator = AgentOrchestrator()

@app.post("/execute_task")
async def execute_task(agent_name: str, params: dict):
    result = await orchestrator.execute_task(agent_name, params)
    return {"result": result}

# Additional endpoints for other orchestrator functions...
