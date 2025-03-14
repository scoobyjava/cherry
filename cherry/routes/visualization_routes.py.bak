from flask import Blueprint, render_template, jsonify

visualization_bp = Blueprint('visualization', __name__, template_folder='../templates/visualization')

@visualization_bp.route('/')
def index():
    """Main visualization page"""
    return render_template('visualization/index.html')

@visualization_bp.route('/agent-network')
def agent_network():
    """Agent network visualization page"""
    return render_template('visualization/agent_network.html')

@visualization_bp.route('/api/agent-network')
def agent_network_data():
    """API endpoint to get agent network data"""
    # Mock data for visualization
    return jsonify({
        "nodes": [
            {"id": "cherry_core", "group": 1, "size": 30},
            {"id": "code_agent", "group": 2, "size": 20},
            {"id": "uiux_agent", "group": 2, "size": 20},
            {"id": "research_agent", "group": 2, "size": 20},
            {"id": "web_scraper", "group": 3, "size": 15},
            {"id": "data_processor", "group": 3, "size": 15}
        ],
        "links": [
            {"source": "cherry_core", "target": "code_agent", "value": 5},
            {"source": "cherry_core", "target": "uiux_agent", "value": 3},
            {"source": "cherry_core", "target": "research_agent", "value": 4},
            {"source": "research_agent", "target": "web_scraper", "value": 2},
            {"source": "web_scraper", "target": "data_processor", "value": 1},
            {"source": "data_processor", "target": "research_agent", "value": 1}
        ]
    })
