from flask import Flask, render_template_string, jsonify
import random
import datetime

app = Flask(__name__)

# Dummy data generators


def get_task_status():
    # Simulate tasks status
    return {"last_task": "Deploy Feature X", "status": "success", "timestamp": datetime.datetime.now().isoformat()}


def get_logs():
    # Simulate logs
    return ["Log entry 1: Task started", "Log entry 2: Task succeeded"]


def get_agent_health():
    # Simulate agent health metrics
    return {"agent": "StagingDeploymentAgent", "cpu": f"{random.randint(1, 50)}%", "memory": f"{random.randint(1, 50)}%"}


@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Cherry Web Interface Prototype</title>
      </head>
      <body>
        <h1>Cherry Dashboard</h1>
        <div id="status">
          <h2>Task Status</h2>
          <pre id="task_status"></pre>
        </div>
        <div id="logs">
          <h2>Logs</h2>
          <pre id="logs_content"></pre>
        </div>
        <div id="agent_health">
          <h2>Agent Health</h2>
          <pre id="health_content"></pre>
        </div>
        <script>
          async function fetchData(endpoint, elementId) {
            const response = await fetch(endpoint);
            const data = await response.json();
            document.getElementById(elementId).textContent = JSON.stringify(data, null, 2);
          }
          fetchData("/api/status", "task_status");
          fetchData("/api/logs", "logs_content");
          fetchData("/api/health", "health_content");
        </script>
      </body>
    </html>
    """
    return render_template_string(html)


@app.route("/api/status")
def api_status():
    return jsonify(get_task_status())


@app.route("/api/logs")
def api_logs():
    return jsonify(get_logs())


@app.route("/api/health")
def api_health():
    return jsonify(get_agent_health())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
