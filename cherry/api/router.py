from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio

from cherry.agents.planning_agent import PlanningAgent

router = APIRouter(prefix="/api", tags=["Cherry Core Endpoints"])

# In-memory chat history storage
chat_history: List[Dict[str, str]] = []

# Instantiate a global PlanningAgent instance
agent = PlanningAgent(name="PlanningAgent",
                      description="Creates development plans and estimates effort.")

# Request models


class ChatRequest(BaseModel):
    task_update: str


class Task(BaseModel):
    id: str
    complexity: int
    deadline: str
    # ...other task attributes if needed...


class TasksScheduleRequest(BaseModel):
    tasks: List[Task]


@router.post("/agent/chat", summary="Send a chat update to the agent and get a personalized response")
async def agent_chat(chat_req: ChatRequest):
    try:
        response = await agent.generate_personalized_response(chat_req.task_update)
        chat_history.append(
            {"update": chat_req.task_update, "response": response})
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/agent/chat/history", summary="Retrieve agent chat history")
async def get_chat_history():
    return {"chat_history": chat_history}


@router.post("/tasks/schedule", summary="Schedule tasks based on complexity and deadlines")
async def schedule_tasks(req: TasksScheduleRequest):
    try:
        # Convert tasks from request to list of dicts
        tasks = [task.dict() for task in req.tasks]
        scheduled = agent.schedule_task(tasks)
        return {"scheduled_tasks": scheduled}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/system/health", summary="Retrieve system health and metrics")
async def system_health():
    try:
        diagnosis = await agent.perform_self_diagnosis()
        return {"system_health": diagnosis}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ...existing code if necessary...
