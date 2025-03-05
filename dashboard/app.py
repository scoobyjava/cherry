from flask import Flask, jsonify, render_template_string
import psutil  # Ensure psutil is installed or replace with another method
import random

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Serve a simple dashboard with JavaScript to fetch metrics
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Dashboard</title>
        <script>
            async function fetchMetrics() {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                document.getElementById('metrics').textContent = JSON.stringify(data, null, 2);
            }
            window.onload = function() {
                fetchMetrics();
                setInterval(fetchMetrics, 5000);
            }
        </script>
    </head>
    <body>
        <h1>System Dashboard</h1>
        <pre id="metrics"></pre>
    </body>
    </html>
    """)

@app.route('/api/metrics')
def api_metrics():
    # Return dummy metrics; replace with real data as needed
    data = {
        "current_tasks": random.randint(0, 10),
        "agent_health": "healthy" if random.random() > 0.2 else "degraded",
        "memory_usage": psutil.virtual_memory().percent if hasattr(psutil, 'virtual_memory') else 0,
        "active_integrations": random.randint(0, 5)
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
