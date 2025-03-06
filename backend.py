from flask import Flask, request, jsonify
from agent_manager import AgentManager
from personality_module import PersonalityModule
from middleware import log_request_time

app = Flask(__name__)
log_request_time(app)  # Integrate request time logging

# Dynamically load agents from the plugins folder and manage personality overlay
agent_manager = AgentManager()
personality = PersonalityModule()


@app.route("/message", methods=["POST"])
def handle_message():
    data = request.get_json()
    user_command = data.get("command", "")
    # e.g., {"private": True, "mode": "casual"}
    user_context = data.get("context", {})
    base_response = "Your task has been processed."
    # Overlay the personality response based on the command and context
    final_response = personality.overlay_response(
        base_response, user_command, user_context)
    # Broadcast the message to agents (each may handle a separate subtask)
    agent_responses = agent_manager.broadcast_message(data)
    return jsonify({
        "final_response": final_response,
        "agent_responses": agent_responses
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
