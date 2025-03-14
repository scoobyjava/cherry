from flask import Blueprint, jsonify

# Create a Blueprint for status routes
status_bp = Blueprint('status', __name__)

@status_bp.route('/')
def get_status():
    """Return system status information"""
    status_info = {
        "system": "operational",
        "agents": {
            "code_agent": "active",
            "uiux_agent": "active",
            "documentation_agent": "active",
            "creative_agent": "idle"
        },
        "services": {
            "database": "connected",
            "api": "operational",
            "message_bus": "operational"
        },
        "uptime": "12h 34m",
        "last_update": "2023-11-15T14:30:00Z"
    }
    return jsonify(status_info)

@status_bp.route('/reviews')
def get_reviews():
    """Return status of active reviews"""
    progress_info = {
        "active_reviews": [
            {
                "id": "review-001",
                "name": "Code Quality Review",
                "status": "in_progress",
                "progress": 65,
                "estimated_completion": "2023-11-15T16:30:00Z",
                "started_at": "2023-11-15T14:30:00Z"
            },
            {
                "id": "review-002",
                "name": "Security Audit",
                "status": "pending",
                "progress": 0,
                "estimated_completion": "2023-11-16T12:00:00Z",
                "started_at": None
            }
        ]
    }
    return jsonify(progress_info)
