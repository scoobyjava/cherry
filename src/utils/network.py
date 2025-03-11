import socket
import logging
import contextlib
from flask import Flask, render_template, jsonify
import time
import threading
from collections import deque

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store recent tasks, errors and status
recent_tasks = deque(maxlen=10)
recent_errors = deque(maxlen=5)
status = "asleep"  # Can be "asleep" or "working"
last_activity = time.time()

# Mock function to simulate tasks (replace with your actual task tracking)


def task_monitor():
    global status, last_activity

    while True:
        # This would be replaced with your actual logic to check Cherry's tasks
        time.sleep(5)

        # If no activity for 30 seconds, set to asleep
        if time.time() - last_activity > 30:
            status = "asleep"


@app.route('/monitor')
def task_monitor_page():
    return render_template('monitor.html')


@app.route('/api/monitor-data')
def monitor_data():
    return jsonify({
        'status': status,
        'tasks': list(recent_tasks),
        'errors': list(recent_errors),
        'last_activity': int(time.time() - last_activity)
    })

# Function to record a new task (call this from your task execution code)


def record_task(task_name, agent_name, result="completed"):
    global status, last_activity
    status = "working"
    last_activity = time.time()
    recent_tasks.appendleft({
        'name': task_name,
        'agent': agent_name,
        'result': result,
        'timestamp': time.time()
    })

# Function to record an error


def record_error(message, source="system"):
    recent_errors.appendleft({
        'message': message,
        'source': source,
        'timestamp': time.time()
    })


# Start the monitoring thread
monitor_thread = threading.Thread(target=task_monitor, daemon=True)
monitor_thread.start()

if __name__ == "__main__":
    app.run(debug=True)


def is_port_available(port: int) -> bool:
    """
    Checks if a given port is available on the local machine.

    Args:
        port: The port number to check.

    Returns:
        True if the port is available, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))  # Try binding to the port
            return True  # If binding succeeds, the port is available
        except OSError as e:
            if e.errno == 98:  # Address already in use
                logger.debug(f"Port {port} is already in use.")
            elif e.errno == 13:  # Permission denied
                logger.warning(
                    f"Permission denied when trying to bind to port {port}.")
            else:
                logger.error(f"An unexpected error occurred: {e}")
            return False  # If binding fails, the port is not available
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return False
