<<<<<<< Tabnine <<<<<<<
from flask import Blueprint, jsonify
from cherry.core.orchestrator import get_orchestrator#-

# Create a Blueprint for status routes#+
status_bp = Blueprint('status', __name__)

#-
@status_bp.route('/status')#-
def system_status():#-
    """Get the current status of Cherry and all agents"""#-
    orchestrator = get_orchestrator()#-
#-
    # Get status information#-
@status_bp.route('/')#+
def get_status():#+
    """Return system status information"""#+
    status_info = {
        "system": {#-
            "status": "active",#-
            "uptime": orchestrator.get_uptime(),#-
            "version": "1.0.0"#-
        },#-
        "system": "operational",#+
        "agents": {
            agent_name: {#-
                "status": agent.status,#-
                "tasks_completed": agent.tasks_completed,#-
                "tasks_pending": agent.tasks_pending#-
            } for agent_name, agent in orchestrator.agents.items()#-
            "code_agent": "active",#+
            "uiux_agent": "active",#+
            "documentation_agent": "active",#+
            "creative_agent": "idle"#+
        },
        "current_reviews": orchestrator.get_active_reviews(),#-
        "completed_reviews": orchestrator.get_completed_reviews()#-
        "services": {#+
            "database": "connected",#+
            "api": "operational",#+
            "message_bus": "operational"#+
        },#+
        "uptime": "12h 34m",#+
        "last_update": "2023-11-15T14:30:00Z"#+
    }
#-
    return jsonify(status_info)

#-
@status_bp.route('/progress')#-
def review_progress():#-
    """Get the progress of current reviews"""#-
    orchestrator = get_orchestrator()#-
@status_bp.route('/reviews')#+
def get_reviews():#+
    """Return status of active reviews"""#+
    progress_info = {
        "active_reviews": [
            {
                "id": review.id,#-
                "status": review.status,#-
                "progress": review.progress,#-
                "estimated_completion": review.estimated_completion_time,#-
                "started_at": review.started_at#-
            } for review in orchestrator.active_reviews#-
                "id": "review-001",#+
                "name": "Code Quality Review",#+
                "status": "in_progress",#+
                "progress": 65,#+
                "estimated_completion": "2023-11-15T16:30:00Z",#+
                "started_at": "2023-11-15T14:30:00Z"#+
            },#+
            {#+
                "id": "review-002",#+
                "name": "Security Audit",#+
                "status": "pending",#+
                "progress": 0,#+
                "estimated_completion": "2023-11-16T12:00:00Z",#+
                "started_at": None#+
            }#+
        ]
    }
#-
    return jsonify(progress_info)
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
