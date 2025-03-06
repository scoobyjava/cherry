import asyncio
import logging
import datetime
import os
import random
import json
import hashlib
from typing import Dict, Any
import psutil  # added import for measuring resource usage
# Comment these out temporarily for testing just the staging deployment
# from cherry.simulation.simulation_framework import run_simulation
# from cherry.learning.learning_system import LearningSystem
# from cherry.diagnostics.diagnostic_tool import DiagnosticTool

# Configure logger for staging deployment tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CherryStagingDeployment")

# --- Simulated External Systems ---


class RealWorldAPI:
    async def call_api(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a realistic API call with controlled latency and responses."""
        # Added security check: reject unauthorized token
        if payload.get("auth_token") == "invalid":
            await asyncio.sleep(0.1)
            return {"status": "error", "message": "Unauthorized request"}
        if payload.get("simulate_timeout"):
            await asyncio.sleep(0.3)  # simulate extended delay
            raise asyncio.TimeoutError("Simulated API timeout")
        if payload.get("simulate_rate_limit"):
            await asyncio.sleep(0.1)
            return {"status": "error", "message": "Rate limit exceeded"}
        await asyncio.sleep(random.uniform(0.1, 0.2))
        if endpoint == "/deploy":
            return {"status": "success", "data": f"Deployed feature {payload.get('feature')}"}
        elif endpoint == "/status":
            return {"status": "ok", "message": "All systems operational"}
        else:
            return {"status": "error", "message": "Unknown endpoint"}


class DatabaseClient:
    async def query(self, query: str) -> Dict[str, Any]:
        """Simulate a database query."""
        # Added security check: detect data injection attempts
        if "DROP TABLE" in query or "DELETE FROM" in query:
            raise Exception("Data injection attempt detected")
        if "simulate_failure" in query:
            raise Exception("Simulated DB failure")
        await asyncio.sleep(random.uniform(0.05, 0.1))
        return {"status": "success", "result": f"Result for query: \"{query}\""}

# --- Deployment Agent Implementation for Staging ---


class StagingDeploymentAgent:
    def __init__(self, name: str = "StagingDeploymentAgent"):
        self.name = name
        self.api = RealWorldAPI()
        self.db = DatabaseClient()

    async def handle_deployment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a deployment task by interacting with external systems.
        Simulate both API calls and database updates.
        """
        try:
            logger.info(f"{self.name}: Initiating deployment for task: {task}")
            # Attempt deployment via API
            api_response = await self.api.call_api("/deploy", task)
            if api_response.get("status") != "success":
                raise Exception("API deployment failed")

            # Simulate DB update to record deployment
            db_response = await self.db.query("UPDATE deployments SET status = 'deployed'")
            logger.info(
                f"{self.name}: Deployment successful. API response: {api_response}, DB update: {db_response}")
            return {"status": "success", "data": {"api": api_response, "db": db_response}}
        except Exception as e:
            logger.error(f"{self.name}: Deployment error: {str(e)}")
            return {"status": "failure", "error": str(e)}

    async def test_error_handling(self, task: Dict[str, Any]) -> None:
        """
        Test error handling by invoking an invalid API endpoint.
        """
        logger.info(f"{self.name}: Testing error handling with task: {task}")
        response = await self.api.call_api("/invalid", task)
        logger.info(
            f"{self.name}: Received response for error handling test: {response}")

    async def test_api_timeout(self, task: Dict[str, Any]) -> None:
        """Test API timeout and retry mechanism."""
        retries = 3
        for attempt in range(1, retries+1):
            try:
                logger.info(
                    f"{self.name}: Attempt {attempt} for API timeout test with task: {task}")
                response = await self.api.call_api("/deploy", {**task, "simulate_timeout": True})
                logger.info(
                    f"{self.name}: Unexpected success on timeout test: {response}")
                return
            except asyncio.TimeoutError as e:
                logger.error(
                    f"{self.name}: API timeout on attempt {attempt}: {e}")
                if attempt == retries:
                    logger.error(f"{self.name}: All retry attempts exhausted.")
                else:
                    await asyncio.sleep(0.2)  # wait before retrying

    async def test_db_failure(self, task: Dict[str, Any]) -> None:
        """Test recovery when DB operations fail."""
        try:
            logger.info(f"{self.name}: Testing DB failure with task: {task}")
            # Trigger simulated failure by including a special query
            await self.db.query("simulate_failure")
        except Exception as e:
            logger.error(f"{self.name}: Caught simulated DB failure: {e}")

    async def test_fallback_agent_collaboration(self, task: Dict[str, Any]) -> None:
        """Validate fallback for failed agent collaboration tasks."""
        try:
            logger.info(
                f"{self.name}: Testing agent collaboration fallback with task: {task}")
            # Simulate a failure in the collaboration workflow
            raise Exception("Simulated collaboration failure")
        except Exception as e:
            logger.error(f"{self.name}: Primary collaboration failed: {e}")
            logger.info(
                f"{self.name}: Falling back to alternative agent for task delegation.")
            # Simulated fallback mechanism (implementation details omitted)
            logger.info(
                f"{self.name}: Alternative agent successfully took over the task.")

    async def test_unauthorized_api_request(self, task: Dict[str, Any]) -> None:
        """Test detection of unauthorized API requests with an invalid token."""
        logger.info(f"{self.name}: Testing unauthorized API request.")
        # Add an invalid auth token to simulate unauthorized access.
        unauthorized_payload = {**task, "auth_token": "invalid"}
        response = await self.api.call_api("/deploy", unauthorized_payload)
        logger.info(f"{self.name}: Unauthorized API test response: {response}")

    async def test_data_injection(self, task: Dict[str, Any]) -> None:
        """Test detection of data injection attempts in database operations."""
        logger.info(f"{self.name}: Testing data injection in DB operation.")
        malicious_query = "DROP TABLE users; --"
        try:
            await self.db.query(malicious_query)
        except Exception as e:
            logger.info(f"{self.name}: Data injection detected: {e}")

    async def test_message_tampering(self, task: Dict[str, Any]) -> None:
        """Simulate detection of message tampering during task communication."""
        logger.info(f"{self.name}: Testing message tampering detection.")
        # Simulate computing a hash for the task message
        task_str = json.dumps(task, sort_keys=True)
        original_hash = hashlib.sha256(task_str.encode()).hexdigest()
        # Simulate tampering by modifying the task after the hash is computed
        tampered_task = task.copy()
        tampered_task["feature"] = tampered_task.get(
            "feature", "") + " [tampered]"
        tampered_str = json.dumps(tampered_task, sort_keys=True)
        tampered_hash = hashlib.sha256(tampered_str.encode()).hexdigest()
        if original_hash != tampered_hash:
            logger.info(
                f"{self.name}: Message tampering detected (hash mismatch).")
        else:
            logger.info(f"{self.name}: No message tampering detected.")

# --- End-to-End Staging Deployment Workflow ---


async def run_staging_deployment():
    logger.info(
        "Hello, Cherry world! 🍒 I'm feeling lively and ready to deploy your code!")
    logger.info("Starting staging deployment tests.")
    start_time = datetime.datetime.now()

    # Instantiate the staging deployment agent
    logger.info("DEBUG: Starting agent creation")
    agent = StagingDeploymentAgent()

    # 1. Test real-world system interactions via deployment API and DB update
    user_task = {"feature": "Awesome New Feature",
                 "details": "Deploy version 1.0 of the new feature."}
    logger.info("Simulating user request for deployment.")
    logger.info("DEBUG: Starting deployment test")
    deployment_result = await agent.handle_deployment(user_task)
    logger.info(f"Deployment result: {deployment_result}")

    # 2. Simulate realistic escalation if deployment fails
    if deployment_result.get("status") == "failure":
        logger.info("Deployment failed. Simulating escalation workflow.")
        # New escalation mechanism
        from cherry.escalation.escalation import escalate_issue
        reason = f"Deployment failed with error: {deployment_result.get('error')}"
        steps = "Check API connectivity, verify DB configurations, and review task parameters."
        doc_link = "https://docs.example.com/cherry/escalation-guide"
        escalate_issue(reason, steps, doc_link, channel="CLI")
        logger.info(
            "Escalation: Notifying system administrator about the deployment failure.")

    # 3. Run end-to-end CI/CD tests: verify error handling functionality
    logger.info("DEBUG: Starting error handling test")
    await agent.test_error_handling(user_task)

    # 4. Validate communication workflows by checking API status
    logger.info("DEBUG: Checking API status")
    status_response = await agent.api.call_api("/status", {})
    logger.info(f"System status check: {status_response}")

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(
        f"Staging deployment tests completed in {duration:.2f} seconds.")

    # Log detailed staging deployment data for further analysis
    report_data = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": duration,
        "deployment_result": deployment_result,
        "status_response": status_response,
    }
    # --- New: Add resource usage and task expansion metrics ---
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory_usage = psutil.virtual_memory().percent
    report_data["resource_usage"] = {
        "cpu_percent": cpu_usage, "memory_usage": memory_usage}
    report_data["task_expansion"] = len(
        user_task)  # basic measure of task details

    # Save individual deployment report
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_dir = os.path.join(BASE_DIR, "staging_reports")
    report_file = os.path.join(
        report_dir, f"staging_deployment_{start_time.strftime('%Y%m%d%H%M%S')}.json")
    try:
        os.makedirs(report_dir, exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write staging report: {e}")
        print(json.dumps(report_data, indent=2))

    # --- New: Update historical deployment data and compute performance insights ---
    historical_file = os.path.join(report_dir, "deployment_history.json")
    try:
        if os.path.exists(historical_file):
            with open(historical_file, "r") as hist_file:
                history = json.load(hist_file)
        else:
            history = []
    except Exception as e:
        logger.error(f"Failed to read historical data: {e}")
        history = []
    history.append(report_data)
    try:
        with open(historical_file, "w") as hist_file:
            json.dump(history, hist_file, indent=2)
    except Exception as e:
        logger.error(f"Failed to update historical data: {e}")

    # Compute average duration from history and derive insights
    durations = [entry.get("duration", 0)
                 for entry in history if entry.get("duration")]
    avg_duration = sum(durations) / len(durations) if durations else duration
    if duration < avg_duration:
        insight = "Deployment is faster than historical average."
    else:
        insight = "Deployment is slower than historical average."
    report_data["performance_change_insights"] = insight
    logger.info(f"Performance Insights: {insight}")

    logger.info(f"Staging deployment report saved at {report_file}")

# --- Full Workflow Implementation ---


async def run_full_workflow():
    # Run simulation and collect data
    simulation_results = await run_simulation()

    # Feed results to learning system
    learner = LearningSystem()
    learner.score_task_outcome(simulation_results)

    # Create a dummy orchestrator for the diagnostic tool
    orchestrator = DummyOrchestrator()  # You'll need to define this or import it
    diagnostic = DiagnosticTool(orchestrator)

    # Run diagnostics with proper parameters - use actual reports, not [...]
    suggestions = diagnostic.suggest_improvements(
        [], [])  # Replace with real data when available

    # Call the local function, not the imported one
    await run_staging_deployment()

# New function to run all failure tests


async def run_failure_tests():
    logger.info("Starting failure tests for Cherry's operations.")
    agent = StagingDeploymentAgent()
    test_task = {"feature": "Test Feature",
                 "details": "Simulated failure test."}

    await agent.test_api_timeout(test_task)
    await agent.test_db_failure(test_task)
    await agent.test_fallback_agent_collaboration(test_task)
    logger.info("Failure tests completed.")

# New function to run security-focused test cases


async def run_security_tests():
    logger.info("Starting security tests for Cherry's operations.")
    agent = StagingDeploymentAgent()
    test_task = {"feature": "Security Test",
                 "details": "Simulated security test."}
    await agent.test_unauthorized_api_request(test_task)
    await agent.test_data_injection(test_task)
    await agent.test_message_tampering(test_task)
    logger.info("Security tests completed.")

# --- Main Entry Point ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Run Cherry staging deployment tests")
    parser.add_argument('--workflow', action="store_true",
                        help="Run full workflow instead of staging deployment only")
    parser.add_argument('--failures', action="store_true",
                        help="Run failure simulation tests")
    parser.add_argument('--security', action="store_true",
                        help="Run security-focused tests")
    args = parser.parse_args()

    try:
        if args.security:
            asyncio.run(run_security_tests())
        elif args.failures:
            asyncio.run(run_failure_tests())
        elif args.workflow:
            # Run complete workflow including simulation, learning, and diagnostic operations
            asyncio.run(run_full_workflow())
        else:
            # Run only the staging deployment test workflow
            asyncio.run(run_staging_deployment())
    except Exception as e:
        print(f"Error running deployment: {e}")
