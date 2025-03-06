import os
import importlib.util
import logging
from flask import Flask, request, jsonify

logger = logging.getLogger("AgentManager")
logger.setLevel(logging.INFO)


class AgentManager:
    def __init__(self, plugins_dir: str = "./agents"):
        self.plugins_dir = plugins_dir
        self.agents = {}
        self.load_agents()

    def load_agents(self):
        # Load all plugins from the agents folder
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith("_agent.py"):
                module_path = os.path.join(self.plugins_dir, filename)
                module_name = filename[:-3]
                spec = importlib.util.spec_from_file_location(
                    module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Expect each plugin to expose a class that inherits from AgentInterface.
                for attr in dir(module):
                    cls = getattr(module, attr)
                    try:
                        # Check if it's a subclass of AgentInterface (imported from agent_interface.py)
                        if isinstance(cls, type) and issubclass(cls, module.agent_interface.AgentInterface) and cls != module.agent_interface.AgentInterface:
                            agent_instance = cls()
                            self.agents[agent_instance.name] = agent_instance
                            agent_instance.start()
                            logger.info(f"Loaded agent: {agent_instance.name}")
                    except Exception as e:
                        logger.error(
                            f"Error loading agent from {filename}: {e}")

    def broadcast_message(self, message: dict) -> dict:
        responses = {}
        for agent_name, agent in self.agents.items():
            try:
                responses[agent_name] = agent.handle_message(message)
            except Exception as e:
                responses[agent_name] = {"error": str(e)}
        return responses


# Initialize Flask for RESTful communication.
app = Flask(__name__)
manager = AgentManager()


@app.route("/agents/message", methods=["POST"])
def send_message():
    """
    Endpoint to send a message to all agents.
    Expects JSON payload: {"sender": "external", "command": "do_task", "payload": {...}}
    """
    message = request.get_json()
    responses = manager.broadcast_message(message)
    return jsonify(responses)


@app.route("/agents/status", methods=["GET"])
def status():
    """
    Endpoint to check status of all agents.
    """
    status_info = {name: "active" for name in manager.agents.keys()}
    return jsonify(status_info)


if __name__ == "__main__":
    # Run in debug mode for development; switch to production WSGI server later.
    app.run(host="0.0.0.0", port=5000)
