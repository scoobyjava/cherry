<<<<<<< Tabnine <<<<<<<
from flask import Blueprint, jsonify, render_template#-
from cherry.feedback.system_evaluator import SystemEvaluator#-
from flask import Blueprint, render_template, jsonify#+

visualization_bp = Blueprint('visualization', __name__)#-
system_evaluator = SystemEvaluator()#-
visualization_bp = Blueprint('visualization', __name__, template_folder='../templates/visualization')#+

@visualization_bp.route('/')#+
def index():#+
    """Main visualization page"""#+
    return render_template('visualization/index.html')#+

@visualization_bp.route('/metrics')#-
def metrics():#-
    # Example metrics data#-
    metrics_data = {#-
        "agent_performance": {#-
            "code_agent": 0.92,#-
            "uiux_agent": 0.87,#-
            "documentation_agent": 0.95,#-
            "creative_agent": 0.89#-
        },#-
        "system_health": {#-
            "memory_usage": 0.45,#-
            "cpu_usage": 0.32,#-
            "response_time": 0.78#-
        }#-
    }#-
    return jsonify(metrics_data)#-
@visualization_bp.route('/agent-network')
def agent_network():
    # Example agent network data#-
    network_data = {#-
    """Agent network visualization page"""#+
    return render_template('visualization/agent_network.html')#+
#+
@visualization_bp.route('/api/agent-network')#+
def agent_network_data():#+
    """API endpoint to get agent network data"""#+
    # Mock data for visualization#+
    return jsonify({#+
        "nodes": [
            {"id": "code_agent", "group": 1, "size": 25},#-
            {"id": "cherry_core", "group": 1, "size": 30},#+
            {"id": "code_agent", "group": 2, "size": 20},#+
            {"id": "uiux_agent", "group": 2, "size": 20},
            {"id": "documentation_agent", "group": 1, "size": 18},#-
            {"id": "creative_agent", "group": 3, "size": 15},#-
            {"id": "orchestrator", "group": 4, "size": 30}#-
            {"id": "research_agent", "group": 2, "size": 20},#+
            {"id": "web_scraper", "group": 3, "size": 15},#+
            {"id": "data_processor", "group": 3, "size": 15}#+
        ],
        "links": [
            {"source": "orchestrator", "target": "code_agent", "value": 10},#-
            {"source": "orchestrator", "target": "uiux_agent", "value": 8},#-
            {"source": "orchestrator", "target": "documentation_agent", "value": 6},#-
            {"source": "orchestrator", "target": "creative_agent", "value": 5},#-
            {"source": "code_agent", "target": "uiux_agent", "value": 7},#-
            {"source": "code_agent", "target": "documentation_agent", "value": 9},#-
            {"source": "uiux_agent", "target": "creative_agent", "value": 4}#-
            {"source": "cherry_core", "target": "code_agent", "value": 5},#+
            {"source": "cherry_core", "target": "uiux_agent", "value": 3},#+
            {"source": "cherry_core", "target": "research_agent", "value": 4},#+
            {"source": "research_agent", "target": "web_scraper", "value": 2},#+
            {"source": "web_scraper", "target": "data_processor", "value": 1},#+
            {"source": "data_processor", "target": "research_agent", "value": 1}#+
        ]
    }#-
    return jsonify(network_data)#-
#-
#-
@visualization_bp.route('/view/agent-network')#-
def view_agent_network():#-
    """Render the agent network visualization page"""#-
    return render_template('visualization/agent_network.html')#-
    })#+
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
