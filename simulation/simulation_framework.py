import asyncio
import logging
import random
import datetime
import os
import json
from typing import Dict, Any, List

logger = logging.getLogger("CherrySimulation")
logging.basicConfig(level=logging.INFO)


class SimulatedEnvironment:
    """Creates a controlled environment to test Cherry's capabilities"""

    def __init__(self):
        self.mock_apis = {}
        self.mock_databases = {}

    async def create_sandboxed_apis(self):
        """Create mock APIs that behave like real ones but in a controlled way"""
        self.mock_apis["code"] = self._create_code_api()
        self.mock_apis["data"] = self._create_data_api()
        return self.mock_apis

    def _create_code_api(self):
        """Create a mock code processing API"""
        async def code_api(request):
            await asyncio.sleep(random.uniform(0.1, 0.3))
            if "error" in request.lower():
                return {"status": "error", "message": "Code contains syntax errors"}
            return {"status": "success", "result": "Code processed successfully"}
        return code_api

    def _create_data_api(self):
        """Create a mock data processing API"""
        async def data_api(request):
            await asyncio.sleep(random.uniform(0.05, 0.2))
            if len(request) > 1000:  # Simulate large payload issues
                return {"status": "error", "message": "Payload too large"}
            return {"status": "success", "processed_items": len(request)}
        return data_api

    async def simulate_user_request(self, request_type="code_fix"):
        """Generate realistic user requests based on type"""
        await asyncio.sleep(0.05)  # Simulate thinking time

        requests = {
            "code_fix": {
                "type": "code_fix",
                "language": random.choice(["python", "javascript", "java"]),
                "complexity": random.choice(["simple", "medium", "complex"]),
                # Sometimes send bad code
                "code": "def example(): print('Hello world')" if random.random() > 0.2 else "def example() print('Hello world')"
            },
            "feature_design": {
                "type": "feature_design",
                "domain": random.choice(["web", "data", "mobile"]),
                "scope": random.choice(["small", "medium", "large"]),
                "requirements": ["User authentication", "Data visualization"]
            },
            "deployment": {
                "type": "deployment",
                "target": random.choice(["staging", "production"]),
                "component": random.choice(["frontend", "backend", "database"]),
                "version": f"1.{random.randint(0,9)}.{random.randint(0,9)}"
            }
        }

        return requests.get(request_type, requests["code_fix"])


async def run_simulation():
    """Main entry point for simulation - called from integration workflows"""
    logger.info("Starting Cherry simulation...")

    # Initialize metrics collection
    metrics = {
        "start_time": datetime.datetime.now().isoformat(),
        "tasks": [],
        "success_count": 0,
        "failure_count": 0,
        "avg_response_time": 0
    }

    # Create simulated environment
    env = SimulatedEnvironment()
    apis = await env.create_sandboxed_apis()

    # Generate a mix of user requests
    request_types = ["code_fix", "feature_design",
                     "deployment"] * 2  # 6 requests in total
    total_time = 0

    for req_type in request_types:
        start_time = datetime.datetime.now()
        user_request = await env.simulate_user_request(req_type)

        # Process the request based on type
        if req_type == "code_fix":
            response = await apis["code"](user_request["code"])
        elif req_type == "feature_design":
            response = {"status": "success",
                        "design": "Proposed design schema"}
        else:  # deployment
            response = await apis["data"](str(user_request))

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        total_time += duration

        task_record = {
            "request_type": req_type,
            "request_data": user_request,
            "response": response,
            "duration": duration,
            "success": response.get("status") == "success"
        }

        metrics["tasks"].append(task_record)
        if task_record["success"]:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1

        logger.info(
            f"Processed {req_type} request in {duration:.2f}s with status: {response.get('status')}")

    # Calculate final metrics
    metrics["end_time"] = datetime.datetime.now().isoformat()
    metrics["total_duration"] = total_time
    metrics["avg_response_time"] = total_time / len(request_types)
    metrics["success_rate"] = (
        metrics["success_count"] / len(request_types)) * 100

    # Save simulation report
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_dir = os.path.join(BASE_DIR, "simulation_reports")
    os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    report_file = os.path.join(report_dir, f"simulation_{timestamp}.json")

    with open(report_file, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(
        f"Simulation complete with {metrics['success_rate']}% success rate")
    logger.info(f"Report saved to {report_file}")

    return metrics

# For direct execution
if __name__ == "__main__":
    asyncio.run(run_simulation())
