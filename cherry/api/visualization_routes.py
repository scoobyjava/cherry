from flask import Blueprint, jsonify, current_app
import os
from ..feedback.system_evaluator import SystemEvaluator

visualization_bp = Blueprint('visualization', __name__, url_prefix='/api/visualization')

@visualization_bp.route('/metrics')
def get_metrics():
    """Return mock visualization metrics"""
    return jsonify({
        "agent_activity": {
            "code_agent": 42,
            "uiux_agent": 28,
            "documentation_agent": 35,
            "creative_agent": 19
        },
        "task_distribution": {
            "completed": 67,
            "in_progress": 23,
            "pending": 10
        }
    })


@visualization_bp.route('/api/agent-network', methods=['GET'])
def get_agent_network():
    """Return the latest agent network visualization"""
    try:
        # Get or create system evaluator
        evaluator = getattr(current_app, 'system_evaluator', None)
        if not evaluator:
            evaluator = SystemEvaluator()
            current_app.system_evaluator = evaluator

        # Generate visualization
        image_path = evaluator._visualize_agent_network()

        if not image_path:
            return jsonify({
                "status": "error",
                "message": "No agent network data available or visualization failed"
            }), 404

        # Convert to relative URL
        image_url = f"/static/reports/{os.path.basename(image_path)}"

        return jsonify({
            "status": "success",
            "image_url": image_url,
            "generated_at": os.path.getmtime(image_path)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
