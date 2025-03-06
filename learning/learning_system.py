import logging
import datetime
import random
from typing import Dict, Any, List, Tuple
import json
import os
from collections import Counter
import glob

from learning.test_generator import TestGenerator

logger = logging.getLogger("CherryLearning")
logging.basicConfig(level=logging.INFO)


class LearningSystem:
    """
    Learning system that analyzes simulation and staging reports to identify
    patterns, optimize workflows, and suggest improvements.
    """

    def __init__(self, reports_dir: str = None):
        """Initialize the learning system with paths to report directories"""
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.reports_dir = reports_dir or self.base_dir
        self.simulation_reports_dir = os.path.join(
            self.base_dir, "simulation_reports")
        self.staging_reports_dir = os.path.join(
            self.base_dir, "staging_reports")

        # Store historical analysis data
        self.history = []

        # Create log directory
        self.log_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def analyze_simulation_reports(self, limit: int = 5) -> Dict[str, Any]:
        """
        Analyze recent simulation reports to extract patterns and insights
        """
        reports = self._get_latest_reports(self.simulation_reports_dir, limit)
        if not reports:
            logger.warning("No simulation reports found for analysis")
            return {}

        analysis = {
            "total_reports": len(reports),
            "avg_success_rate": 0,
            "avg_response_time": 0,
            "common_failures": {},
            "insights": []
        }

        # Calculate average metrics
        success_rates = []
        response_times = []
        failures = []

        for report_path in reports:
            try:
                with open(report_path, 'r') as f:
                    report = json.load(f)

                success_rate = report.get("success_rate", 0)
                success_rates.append(success_rate)

                response_time = report.get("avg_response_time", 0)
                response_times.append(response_time)

                # Collect failures for pattern analysis
                for task in report.get("tasks", []):
                    if not task.get("success", True):
                        failures.append({
                            "type": task.get("request_type", "unknown"),
                            "response": task.get("response", {})
                        })
            except Exception as e:
                logger.error(f"Error analyzing report {report_path}: {e}")

        # Calculate averages
        if success_rates:
            analysis["avg_success_rate"] = sum(
                success_rates) / len(success_rates)
        if response_times:
            analysis["avg_response_time"] = sum(
                response_times) / len(response_times)

        # Analyze failures by type
        failure_types = {}
        for failure in failures:
            failure_type = failure.get("type", "unknown")
            failure_types[failure_type] = failure_types.get(
                failure_type, 0) + 1

        analysis["common_failures"] = failure_types

        # Generate insights
        if analysis["avg_success_rate"] < 90:
            analysis["insights"].append(
                f"Low success rate ({analysis['avg_success_rate']:.1f}%). Consider improving error handling.")

        if failure_types:
            most_common = max(failure_types.items(), key=lambda x: x[1])[0]
            analysis["insights"].append(
                f"Most common failure type: {most_common}. Review handling for this scenario.")

        logger.info(
            f"Completed simulation analysis: {len(reports)} reports, {analysis['avg_success_rate']:.1f}% success")
        return analysis

    def analyze_staging_reports(self, limit: int = 5) -> Dict[str, Any]:
        """
        Analyze recent staging reports to extract deployment patterns and insights
        """
        reports = self._get_latest_reports(self.staging_reports_dir, limit)
        if not reports:
            logger.warning("No staging reports found for analysis")
            return {}

        analysis = {
            "total_reports": len(reports),
            "avg_duration": 0,
            "resource_usage": {"cpu": 0, "memory": 0},
            "insights": []
        }

        durations = []
        cpu_usage = []
        memory_usage = []

        for report_path in reports:
            try:
                with open(report_path, 'r') as f:
                    report_data = json.load(f)

                # Fix for the deployment_history.json issue - check data type
                if isinstance(report_data, list):
                    # Handle list format - likely deployment_history.json
                    logger.info(
                        f"Found list-formatted report in {report_path}")
                    continue  # Skip this report or process it differently

                # Process dictionary-formatted reports
                if isinstance(report_data, dict):
                    durations.append(report_data.get("duration", 0))

                    resource = report_data.get("resource_usage", {})
                    if resource and isinstance(resource, dict):
                        cpu_usage.append(resource.get("cpu_percent", 0))
                        memory_usage.append(resource.get("memory_usage", 0))

            except Exception as e:
                logger.error(
                    f"Error analyzing staging report {report_path}: {e}")

        # Calculate averages
        if durations:
            analysis["avg_duration"] = sum(durations) / len(durations)
        if cpu_usage:
            analysis["resource_usage"]["cpu"] = sum(cpu_usage) / len(cpu_usage)
        if memory_usage:
            analysis["resource_usage"]["memory"] = sum(
                memory_usage) / len(memory_usage)

        # Generate insights
        if analysis["avg_duration"] > 1.0:  # If average duration exceeds 1 second
            analysis["insights"].append(
                f"Deployment taking {analysis['avg_duration']:.2f}s on average. Consider optimizing.")

        if analysis["resource_usage"]["memory"] > 70:  # If memory usage exceeds 70%
            analysis["insights"].append(
                "High memory usage detected. Review memory allocation.")

        logger.info(
            f"Completed staging analysis: {len(reports)} reports, avg duration {analysis['avg_duration']:.2f}s")
        return analysis

    def suggest_improvements(self) -> List[str]:
        """
        Based on analysis of simulation and staging reports, suggest improvements
        to Cherry's systems and workflows.
        """
        simulation_analysis = self.analyze_simulation_reports()
        staging_analysis = self.analyze_staging_reports()

        suggestions = []

        # Add insights from both analyses
        suggestions.extend(simulation_analysis.get("insights", []))
        suggestions.extend(staging_analysis.get("insights", []))

        # Cross-analysis suggestions
        sim_success_rate = simulation_analysis.get("avg_success_rate", 100)
        staging_duration = staging_analysis.get("avg_duration", 0)

        if sim_success_rate < 95 and staging_duration > 0.5:
            suggestions.append(
                "Both success rate and deployment speed need improvement. Consider a comprehensive review.")

        # If few failures, suggest expanding test coverage
        if sim_success_rate > 98:
            suggestions.append(
                "High success rate detected. Consider adding more edge cases to testing.")

        # Log the analysis and suggestions
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_file = os.path.join(
            self.log_dir, f"learning_analysis_{timestamp}.json")

        analysis_log = {
            "timestamp": datetime.datetime.now().isoformat(),
            "simulation_analysis": simulation_analysis,
            "staging_analysis": staging_analysis,
            "suggestions": suggestions
        }

        with open(log_file, "w") as f:
            json.dump(analysis_log, f, indent=2)

        logger.info(
            f"Learning analysis complete with {len(suggestions)} suggestions")
        logger.info(f"Analysis log saved to {log_file}")

        return suggestions

    def generate_test_cases(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate test cases based on learning from past reports"""
        generator = TestGenerator(self.simulation_reports_dir)
        test_cases = generator.generate_tests(count)

        logger.info(
            f"Generated {len(test_cases)} new test cases based on past patterns")
        return test_cases

    def _get_latest_reports(self, directory: str, limit: int) -> List[str]:
        """Get the latest reports from a directory, sorted by timestamp"""
        pattern = os.path.join(directory, "*.json")
        reports = glob.glob(pattern)
        # Sort by file modification time (most recent first)
        reports.sort(key=os.path.getmtime, reverse=True)
        return reports[:limit]


# Direct execution
if __name__ == "__main__":
    logger.info("Initializing Cherry Learning System")
    learner = LearningSystem()
    suggestions = learner.suggest_improvements()
    print("\n=== Cherry Learning System Suggestions ===")
    for idx, suggestion in enumerate(suggestions, 1):
        print(f"{idx}. {suggestion}")
