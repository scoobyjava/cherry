from flask import Flask
from cherry.routes.visualization_routes import visualization_bp
from cherry.routes.status_routes import status_bp
# Import other blueprints

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(visualization_bp, url_prefix='/visualization')
    app.register_blueprint(status_bp, url_prefix='/status')
    # Register other blueprints

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

    # Ensure static directories exist
    os.makedirs(os.path.join(app.static_folder, 'reports'), exist_ok=True)
    os.makedirs('cherry/templates', exist_ok=True)
    os.makedirs('cherry/static/css', exist_ok=True)
    os.makedirs('cherry/static/js', exist_ok=True)
    os.makedirs('cherry/static/reports', exist_ok=True)

    # Create empty dashboard template if it doesn't exist
    if not os.path.exists('cherry/templates/dashboard.html'):
        open('cherry/templates/dashboard.html', 'a').close()

    # Create empty index template if it doesn't exist
    if not os.path.exists('cherry/templates/index.html'):
        open('cherry/templates/index.html', 'a').close()

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/')
    def index():
        return render_template('index.html')

    # Mock API endpoints for development
    @app.route('/api/tasks')
    def get_tasks():
        # Mock data for active tasks
        tasks = [
            {
                "id": "task-001",
                "name": "Code Generation",
                "status": "in_progress",
                "assigned_to": "code_agent",
                "priority": "high",
                "completion": 65,
                "created_at": "2023-11-15T10:30:00Z"
            },
            {
                "id": "task-002",
                "name": "UI Component Design",
                "status": "pending",
                "assigned_to": "uiux_agent",
                "priority": "medium",
                "completion": 0,
                "created_at": "2023-11-15T11:45:00Z"
            },
            {
                "id": "task-003",
                "name": "API Documentation",
                "status": "completed",
                "assigned_to": "documentation_agent",
                "priority": "low",
                "completion": 100,
                "created_at": "2023-11-14T09:15:00Z"
            }
        ]
        return jsonify({"tasks": tasks})

    @app.route('/api/leaderboard')
    def get_leaderboard():
        # Mock data for agent performance
        agents = [
            {
                "name": "code_agent",
                "success_rate": 92.5,
                "avg_response_time": 1.2,
                "efficiency_score": 87.3,
                "tasks_handled": 45,
                "specialization": "Backend Development"
            },
            {
                "name": "uiux_agent",
                "success_rate": 88.7,
                "avg_response_time": 0.9,
                "efficiency_score": 85.1,
                "tasks_handled": 32,
                "specialization": "Frontend Design"
            },
            {
                "name": "documentation_agent",
                "success_rate": 95.2,
                "avg_response_time": 0.7,
                "efficiency_score": 91.8,
                "tasks_handled": 28,
                "specialization": "Technical Writing"
            },
            {
                "name": "creative_agent",
                "success_rate": 84.3,
                "avg_response_time": 1.5,
                "efficiency_score": 79.6,
                "tasks_handled": 21,
                "specialization": "Creative Solutions"
            }
        ]
        return jsonify({"agents": agents})

    @app.route('/api/agent-network')
    def get_agent_network():
        # Mock data for agent network visualization
        nodes = [
            {"id": "code_agent", "group": 1, "size": 25},
            {"id": "uiux_agent", "group": 2, "size": 20},
            {"id": "documentation_agent", "group": 1, "size": 18},
            {"id": "creative_agent", "group": 3, "size": 15},
            {"id": "orchestrator", "group": 4, "size": 30}
        ]

        links = [
            {"source": "orchestrator", "target": "code_agent", "value": 10},
            {"source": "orchestrator", "target": "uiux_agent", "value": 8},
            {"source": "orchestrator", "target": "documentation_agent", "value": 6},
            {"source": "orchestrator", "target": "creative_agent", "value": 5},
            {"source": "code_agent", "target": "uiux_agent", "value": 7},
            {"source": "code_agent", "target": "documentation_agent", "value": 9},
            {"source": "uiux_agent", "target": "creative_agent", "value": 4}
        ]

        return jsonify({"nodes": nodes, "links": links})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
