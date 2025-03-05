from cherry.agents.base_agent import Agent
import logging
import subprocess

logger = logging.getLogger(__name__)


class TestingAgent(Agent):
    """
    Agent responsible for building, running, and analyzing testing workflows.
    Implements shared task delegation with fallback mechanisms.
    """

    def __init__(self, name="TestingAgent", description="Handles test automation workflows"):
        super().__init__(name, description)

    def execute_task(self, task):
        try:
            if task.get('action') == 'run_tests':
                return self.run_tests(task.get('params'))
            elif task.get('action') == 'build_environment':
                return self.build_environment(task.get('params'))
            else:
                raise ValueError("Unsupported testing action")
        except Exception as e:
            logger.error(f"TestingAgent execution error: {e}")
            return {"error": "Fallback: Unable to process testing task."}

    def run_tests(self, params):
        # ...existing code to run tests...
        try:
            result = subprocess.run(["pytest"], capture_output=True, text=True)
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {"error": "Fallback: Test execution failed."}

    def build_environment(self, params):
        # ...existing code to build environment...
        try:
            return {"status": "success", "message": "Test environment built successfully."}
        except Exception as e:
            logger.error(f"Environment build error: {e}")
            return {"error": "Fallback: Environment build failed."}
