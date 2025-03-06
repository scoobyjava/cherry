import random
import json
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CherryTestGenerator")


class TestGenerator:
    """Generates new test cases based on learning from previous runs"""

    def __init__(self, reports_dir: Optional[str] = None):
        """Initialize with path to reports directory"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.reports_dir = reports_dir or os.path.join(
            base_dir, "simulation_reports")
        self.templates = {
            "code_fix": self._generate_code_fix_test,
            "feature_design": self._generate_feature_design_test,
            "deployment": self._generate_deployment_test
        }

    def generate_tests(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate a set of new test cases based on past reports"""
        test_cases = []
        past_patterns = self._analyze_past_reports()

        # Generate requested number of tests
        for _ in range(count):
            test_type = self._select_test_type(past_patterns)
            generator = self.templates.get(test_type)
            if generator:
                test_case = generator(past_patterns)
                test_cases.append(test_case)

        return test_cases

    def _analyze_past_reports(self) -> Dict[str, Any]:
        """Analyze past reports to identify patterns for test generation"""
        patterns = {
            "code_fix": {
                "languages": [],
                "common_errors": [],
                "complexity": []
            },
            "feature_design": {
                "domains": [],
                "requirements": [],
                "scope": []
            },
            "deployment": {
                "targets": [],
                "components": []
            },
            "failure_patterns": [],
            "success_patterns": []
        }

        # Scan available reports
        for filename in os.listdir(self.reports_dir):
            if not filename.endswith('.json'):
                continue

            try:
                with open(os.path.join(self.reports_dir, filename), 'r') as f:
                    report = json.load(f)

                # Extract task data
                for task in report.get("tasks", []):
                    task_type = task.get("request_type")
                    request_data = task.get("request_data", {})

                    if task_type == "code_fix":
                        patterns["code_fix"]["languages"].append(
                            request_data.get("language", "python"))
                        # Extract common errors if any
                        if not task.get("success", True):
                            patterns["failure_patterns"].append(request_data)

                    elif task_type == "feature_design":
                        patterns["feature_design"]["domains"].append(
                            request_data.get("domain", "web"))
                        patterns["feature_design"]["requirements"].extend(
                            request_data.get("requirements", []))

                    elif task_type == "deployment":
                        patterns["deployment"]["targets"].append(
                            request_data.get("target", "staging"))
                        patterns["deployment"]["components"].append(
                            request_data.get("component", "backend"))

            except Exception as e:
                logger.error(
                    f"Error analyzing report for test generation: {e}")

        # Deduplicate lists
        for category, items in patterns.items():
            if isinstance(items, dict):
                for key, values in items.items():
                    if isinstance(values, list):
                        patterns[category][key] = list(set(values))

        return patterns

    def _select_test_type(self, patterns: Dict[str, Any]) -> str:
        """Select a test type, potentially focusing on areas with failures"""
        # Weighted selection based on past failures
        if patterns["failure_patterns"] and random.random() < 0.7:
            # Look at past failure types
            failure_types = [
                f.get("type") for f in patterns["failure_patterns"] if isinstance(f, dict)]
            if failure_types:
                # Select from failure types
                return max(set(failure_types), key=failure_types.count)

        # Default selection
        return random.choice(["code_fix", "feature_design", "deployment"])

    def _generate_code_fix_test(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a code fix test case"""
        languages = patterns["code_fix"]["languages"] or [
            "python", "javascript", "java"]
        language = random.choice(languages)

        # Generate code with errors based on language
        if language == "python":
            # Create Python code with common syntax errors
            errors = [
                "def function(x, y): return x + + y",
                "for i in range(10) print(i)",
                "if x == 5 return True",
                "class Test: def __init__(self) self.x = 1"
            ]
            code = random.choice(errors)
        elif language == "javascript":
            # Create JavaScript code with errors
            errors = [
                "function test() { return x +* y; }",
                "for(let i=0; i<10, i++) { console.log(i); }",
                "if(x === 5) { return true"
            ]
            code = random.choice(errors)
        else:
            # Generic code with error
            code = f"function brokenFunction() {{ return 'error in {language}' }"

        return {
            "type": "code_fix",
            "language": language,
            "code": code,
            "complexity": random.choice(["simple", "medium", "complex"])
        }

    def _generate_feature_design_test(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a feature design test case"""
        domains = patterns["feature_design"]["domains"] or [
            "web", "mobile", "data"]
        requirements_pool = patterns["feature_design"]["requirements"] or [
            "User authentication", "Data visualization", "Real-time updates",
            "Offline access", "Payment processing", "Social sharing",
            "Cross-platform support", "Dark mode", "Analytics dashboard"
        ]

        # Create a feature design request
        num_requirements = random.randint(2, 5)
        requirements = random.sample(requirements_pool, min(
            num_requirements, len(requirements_pool)))

        return {
            "type": "feature_design",
            "domain": random.choice(domains),
            "scope": random.choice(["small", "medium", "large"]),
            "requirements": requirements
        }

    def _generate_deployment_test(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a deployment test case"""
        targets = patterns["deployment"]["targets"] or [
            "staging", "production", "dev"]
        components = patterns["deployment"]["components"] or [
            "frontend", "backend", "database"]

        # Create a deployment request
        return {
            "type": "deployment",
            "target": random.choice(targets),
            "component": random.choice(components),
            "version": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
        }
