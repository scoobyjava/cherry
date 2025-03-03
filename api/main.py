# api.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from cherry.core.orchestrator import AdvancedOrchestrator
from logger import logger
from memory import memory_storage

router = APIRouter()
orchestrator = None

class TaskRequest(BaseModel):
    description: str
    priority: Optional[int] = 1
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    id: int
    status: str
    message: str

class MessageRequest(BaseModel):
    content: str
    user_id: Optional[str] = "default_user"

class MessageResponse(BaseModel):
    content: str
    task_id: Optional[int] = None

def get_orchestrator():
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="AdvancedOrchestrator not initialized yet.")
    return orchestrator

@router.get("/")
async def root():
    return {"status": "online", "service": "Cherry AI", "version": "0.1.0"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest, orchestrator: AdvancedOrchestrator = Depends(get_orchestrator)):
    task_id = orchestrator.add_task(
        description=task_request.description,
        priority=task_request.priority,
        context=task_request.context
    )
    task_status = orchestrator.get_task_status(task_id)
    memory_storage.add_task(task_status)
    return {"id": task_id, "status": "pending", "message": "Task added to queue"}

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, orchestrator: AdvancedOrchestrator = Depends(get_orchestrator)):
    result = orchestrator.get_task_status(task_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/tasks")
async def get_all_tasks(orchestrator: AdvancedOrchestrator = Depends(get_orchestrator)):
    return orchestrator.get_all_tasks()

@router.delete("/tasks/completed")
async def clear_completed_tasks(orchestrator: AdvancedOrchestrator = Depends(get_orchestrator)):
    orchestrator.clear_completed_tasks()
    return {"status": "success", "message": "Completed tasks cleared"}

@router.post("/generate", response_model=MessageResponse)
async def generate(message_request: MessageRequest, background_tasks: BackgroundTasks, orchestrator: AdvancedOrchestrator = Depends(get_orchestrator)):
    try:
        memory_storage.add_conversation({
            "user_id": message_request.user_id,
            "role": "user",
            "content": message_request.content,
            "timestamp": None
        })

        task_id = orchestrator.add_task(
            description=message_request.content,
            context={"user_id": message_request.user_id}
        )

        response = orchestrator._process_task_with_llm(task=orchestrator.get_task_status(task_id))

        memory_storage.add_conversation({
            "user_id": message_request.user_id,
            "role": "assistant",
            "content": response.get("output", "Sorry, I couldn't process that."),
            "timestamp": None
        })

        return {
            "content": response.get("output", "Sorry, I couldn't process that."),
            "task_id": task_id
        }
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def setup_routes(app, orch_instance):
    global orchestrator
    orchestrator = orch_instance
    app.include_router(router)
    logger.info("API routes initialized")
