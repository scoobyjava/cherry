from flask import Flask, render_template, jsonify
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Dummy data for demonstration
tasks = [
    {"id": 1, "title": "Implement feature X", "status": "in-progress"},
    {"id": 2, "title": "Fix bug Y", "status": "completed"},
    # ...existing tasks...
]

leaderboard = [
    {"agent": "Alice", "tasks_completed": 12, "avg_time": 2.5},
    {"agent": "Bob", "tasks_completed": 9, "avg_time": 3.1},
    # ...existing data...
]


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/tasks")
def get_tasks():
    return jsonify(tasks)


@app.route("/api/leaderboard")
def get_leaderboard():
    return jsonify(leaderboard)


if __name__ == "__main__":
    app.run(debug=True)
