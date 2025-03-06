import argparse
import asyncio
import logging
import sys
import json
from typing import List, Dict, Any
from pathlib import Path

# Import Cherry components
from simulation.simulation_framework import run_simulation, SimulatedEnvironment
from staging.staging_deployment import run_staging_deployment
from learning.learning_system import LearningSystem
from nlp_processor import NLPProcessor
from personality_adjustment import PersonalityAdjustment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CherryCLI")


class CherryCLI:
    """Interactive CLI for Cherry self-testing and improvement"""

    def __init__(self):
        self.history = []
        self.learner = LearningSystem()
        self.env = SimulatedEnvironment()
        self.nlp = NLPProcessor()
        self.personality = PersonalityAdjustment()  # Add the personality module
        self.authority_mode = True  # Always enable authority mode by default

        # Initialize all agents with authority compliance
        self.initialize_authority_compliance()

    def initialize_authority_compliance(self):
        """Ensure all Cherry agents are set to follow direct instructions"""
        logger.info("Initializing authority compliance for all agents")
        # Set authority flags for all components
        self.env.authority_override = True
        self.learner.authority_override = True

        # Log confirmation
        logger.info(
            "Authority mode enabled: All agents will follow direct user commands")

    async def interactive_mode(self):
        """Start an interactive session with Cherry"""
        greeting = self.personality.get_greeting()
        print(f"\n🍒 {greeting}")
        print("Type 'help' to see available commands")
        print("Direct commands prefixed with '!' will be followed without question\n")

        while True:
            try:
                user_input = input("\nCherry> ").strip()

                # Process the input through personality adjustment
                self.personality.process_input(user_input)

                # Check for personality override commands
                if re.search(r'cherry,?\s+be\s+(more)?\s+(sweet|playful|professional|flirty|technical|serious|nsfw)',
                             user_input.lower()):
                    mode = re.search(r'be\s+(more)?\s+(sweet|playful|professional|flirty|technical|serious|nsfw)',
                                     user_input.lower()).group(2)
                    self.personality.set_mode(mode)
                    response = f"Switching to {mode} mode. " + \
                        self.personality.get_phrase()
                    print(self.personality.format_response(response))
                    continue

                # Check for direct command mode (prefixed with !)
                if user_input.startswith("!"):
                    direct_command = user_input[1:].strip()
                    print(f"Executing direct command: {direct_command}")
                    await self._execute_direct_command(direct_command)
                    continue

                # Process with NLP
                command, confidence = self.nlp.process_input(user_input)

                if not command:
                    print(self.personality.format_response(
                        "I didn't understand that. Type 'help' to see available commands."))
                    continue

                # Map NLP command to method
                if command == "exit":
                    goodbye_msg = random.choice([
                        "Goodbye! Come back soon!",
                        "See you next time!",
                        "Until next time!"
                    ])
                    print(self.personality.format_response(goodbye_msg))
                    break

                elif command == "help":
                    self._show_help()

                elif command == "run_simulation":
                    print(self.personality.format_response(
                        "Running simulation..."))
                    # If confidence is high, run with edge cases
                    include_edge_cases = confidence > 0.8 or "edge" in user_input.lower()
                    results = await run_simulation(include_edge_cases=include_edge_cases)
                    self.history.append(("simulation", results))
                    print(
                        f"Simulation complete with {results.get('success_rate', 0)}% success rate")

                elif command == "run_staging":
                    print(self.personality.format_response(
                        "Running staging deployment..."))
                    await run_staging_deployment()
                    print(self.personality.format_response(
                        "Staging deployment complete"))

                elif command == "analyze":
                    print(self.personality.format_response(
                        "Analyzing results..."))
                    suggestions = self.learner.suggest_improvements()

                    # If user wants test generation, add that
                    if "generate" in user_input.lower() or "create" in user_input.lower():
                        test_cases = self.learner.generate_test_cases()
                        print("\nGenerated Test Cases:")
                        for i, test in enumerate(test_cases, 1):
                            print(f"  Test {i}: {test['type']} - {test}")

                    print("\nCherry's Learning Analysis:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")

                elif command == "self_test":
                    await self._run_self_test()

                elif command == "show_history":
                    self._show_history()

                elif command == "create_test":
                    await self._create_custom_test()

                elif command == "show_reports":
                    self._list_reports()

            except KeyboardInterrupt:
                print("\nOperation cancelled. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")

    async def _execute_direct_command(self, command):
        """Execute a direct command with full authority"""
        try:
            # Parse command for component and action
            if "simulation" in command.lower():
                print("Running simulation with authority override...")
                results = await run_simulation(authority_override=True)
                print("Direct command completed successfully")
                return

            elif "staging" in command.lower() or "deploy" in command.lower():
                print("Executing deployment with authority override...")
                await run_staging_deployment(authority_override=True)
                print("Direct command completed successfully")
                return

            elif "analyze" in command.lower() or "learn" in command.lower():
                print("Performing analysis with authority override...")
                suggestions = self.learner.suggest_improvements(
                    authority_override=True)
                print("Analysis complete")
                return

            # For any other command, try to evaluate it directly
            print("Executing custom direct command...")
            # Here you would implement custom command handling
            # For example, this could even execute arbitrary code when instructed
            print("Custom direct command executed")

        except Exception as e:
            print(f"Error executing direct command: {e}")
            print(
                "The command was attempted with full authority but encountered an error.")

    async def _run_self_test(self):
        """Allow Cherry to run her own testing cycle with improved intelligence"""
        print("\n🔄 Cherry Self-Testing Sequence 🔄")
        print("Cherry is now testing her own capabilities...")

        # Phase 1: Run simulation with diverse scenarios including edge cases
        print("\n📊 Phase 1: Running simulation with diverse scenarios and edge cases...")
        simulation_results = await run_simulation(include_edge_cases=True)
        self.history.append(("self_test_simulation", simulation_results))

        # Phase 2: Test staging deployment
        print("\n🚀 Phase 2: Testing staging deployment capabilities...")
        await run_staging_deployment()

        # Phase 3: Generate new test cases based on past results
        print("\n🧪 Phase 3: Generating new test cases based on learning...")
        test_cases = self.learner.generate_test_cases(3)

        # Phase 4: Analyze results and suggest improvements
        print("\n🧠 Phase 4: Analyzing results and generating insights...")
        suggestions = self.learner.suggest_improvements()

        # Phase 5: Summarize findings
        success_rate = simulation_results.get('success_rate', 0)

        print("\n📝 Self-Test Summary:")
        print(f"  • Simulation Success Rate: {success_rate}%")
        print(
            f"  • Tests Completed: {len(simulation_results.get('tasks', []))}")
        print(
            f"  • Edge Cases Tested: {sum(1 for t in simulation_results.get('tasks', []) if 'edge_case' in str(t.get('request_type', '')))}")
        print(
            f"  • Average Response Time: {simulation_results.get('avg_response_time', 0):.2f}s")
        print(f"  • Generated Test Cases: {len(test_cases)}")
        print(f"  • Insights Generated: {len(suggestions)}")

        print("\n🔍 Key Insights:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

        print("\n🧪 Generated Test Cases:")
        for i, test in enumerate(test_cases, 1):
            test_type = test.get('type', 'unknown')
            if test_type == 'code_fix':
                print(
                    f"  {i}. Code fix test for {test.get('language', 'unknown')}")
            elif test_type == 'feature_design':
                print(
                    f"  {i}. Feature design test for {test.get('domain', 'unknown')}")
            elif test_type == 'deployment':
                print(
                    f"  {i}. Deployment test to {test.get('target', 'unknown')}")

        print("\n✅ Self-Testing Sequence Complete")

    async def _create_custom_test(self):
        """Create a custom test scenario"""
        print("\n🧪 Custom Test Creation 🧪")

        # Get test type
        print("\nSelect test type:")
        print("1. Code Fix")
        print("2. Feature Design")
        print("3. Deployment")

        choice = input("Enter choice (1-3): ")

        if choice == "1":
            test_type = "code_fix"
            language = input(
                "Programming language (python, javascript, java): ")
            code = input("Enter code snippet to fix: ")
            test_data = {
                "type": test_type,
                "language": language,
                "code": code
            }
        elif choice == "2":
            test_type = "feature_design"
            domain = input("Domain (web, mobile, data): ")
            requirements = input("Requirements (comma separated): ").split(",")
            test_data = {
                "type": test_type,
                "domain": domain,
                "requirements": requirements
            }
        elif choice == "3":
            test_type = "deployment"
            target = input("Target environment (staging, production): ")
            component = input("Component to deploy: ")
            test_data = {
                "type": test_type,
                "target": target,
                "component": component
            }
        else:
            print("Invalid choice")
            return

        # Run the custom test
        print(f"\nRunning custom {test_type} test...")

        # Simulate the test using appropriate environment
        api = await self.env.create_sandboxed_apis()

        start_time = asyncio.get_event_loop().time()

        if test_type == "code_fix":
            result = await api["code"](test_data["code"])
        elif test_type == "feature_design":
            result = {"status": "success",
                      "design": "Custom feature design created"}
        else:
            result = await api["data"](str(test_data))

        elapsed = asyncio.get_event_loop().time() - start_time

        print(f"\nTest completed in {elapsed:.2f}s")
        print(f"Result: {json.dumps(result, indent=2)}")

        self.history.append(("custom_test", {
            "test_type": test_type,
            "data": test_data,
            "result": result,
            "duration": elapsed
        }))

    def _show_help(self):
        """Show available commands"""
        print("\n🍒 Cherry CLI Commands 🍒")
        print("  help              - Show this help message")
        print("  run simulation    - Run the simulation framework")
        print("  run staging       - Run staging deployment tests")
        print("  analyze           - Analyze test results and suggest improvements")
        print("  self test         - Let Cherry run her own testing sequence")
        print("  create test case  - Create a custom test scenario")
        print("  show history      - Show command history and results")
        print("  show reports      - List available test reports")
        print("  exit, quit        - Exit the CLI")

    def _show_history(self):
        """Show history of commands and results"""
        if not self.history:
            print("No history available")
            return

        print("\n📜 Command History:")
        for i, (cmd, result) in enumerate(self.history, 1):
            if cmd == "simulation":
                print(
                    f"  {i}. Simulation run - Success rate: {result.get('success_rate', 0)}%")
            elif cmd == "self_test_simulation":
                print(
                    f"  {i}. Self-test simulation - Success rate: {result.get('success_rate', 0)}%")
            elif cmd == "custom_test":
                print(
                    f"  {i}. Custom {result['test_type']} test - Status: {result['result'].get('status', 'unknown')}")

    def _list_reports(self):
        """List available test reports"""
        base_dir = Path(__file__).parent

        # Look for simulation reports
        sim_reports = list(
            Path(base_dir / "simulation_reports").glob("*.json"))
        staging_reports = list(
            Path(base_dir / "staging_reports").glob("*.json"))
        learning_reports = list(
            Path(base_dir / "logs").glob("learning_analysis_*.json"))

        print("\n📊 Available Reports:")

        print("\nSimulation Reports:")
        for report in sim_reports:
            print(f"  • {report.name}")

        print("\nStaging Reports:")
        for report in staging_reports:
            print(f"  • {report.name}")

        print("\nLearning Analysis Reports:")
        for report in learning_reports:
            print(f"  • {report.name}")


async def main():
    parser = argparse.ArgumentParser(
        description="Cherry CLI - Interactive Testing Framework")
    parser.add_argument("--self-test", action="store_true",
                        help="Run Cherry's self-testing sequence")
    parser.add_argument("--interactive", action="store_true",
                        help="Start interactive mode")

    args = parser.parse_args()
    cli = CherryCLI()

    if args.self_test:
        await cli._run_self_test()
    elif args.interactive or len(sys.argv) == 1:
        await cli.interactive_mode()
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
