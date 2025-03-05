import os
import subprocess
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    A module to analyze Cherry's codebase, suggest improvements,
    implement approved changes with safety checks, and rollback if needed.
    """

    def run_safety_checks(self) -> bool:
        """
        Check that the git working tree is clean.
        Returns True if safe, False otherwise.
        """
        try:
            status = subprocess.check_output(
                ['git', 'status', '--porcelain']).decode().strip()
            if status:
                logger.error(
                    "Working tree not clean. Please commit or stash changes before proceeding.")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to run safety checks: {e}")
            return False

    def analyze_codebase(self) -> Dict[str, List[str]]:
        """
        Analyze the codebase and generate improvement suggestions.
        Here we simulate static checks and improvement proposals.
        """
        improvements = {
            "cherry/agents/planning_agent.py": [
                "Refactor task breakdown logic for clarity.",
                "Improve error handling in roadmap generation."
            ],
            "cherry/code_analysis": [
                "Modularize self-diagnosis logic for reusability."
            ]
        }
        logger.info("Code analysis completed. Suggestions generated.")
        return improvements

    def apply_changes(self, approved_changes: Dict[str, str]) -> bool:
        """
        Apply approved changes to files.
        approved_changes: Dictionary mapping file paths to new content.
        Commits changes if safety checks are passed.
        """
        if not self.run_safety_checks():
            logger.error("Safety checks failed. Aborting changes.")
            return False

        try:
            for filepath, new_content in approved_changes.items():
                with open(filepath, 'w') as f:
                    f.write(new_content)
                logger.info(f"Applied changes to {filepath}")

            # Stage changes and commit
            subprocess.check_call(['git', 'add', '.'])
            commit_message = "Applied approved code improvements"
            subprocess.check_call(['git', 'commit', '-m', commit_message])
            logger.info("Changes committed successfully.")
            return True
        except Exception as e:
            logger.error(f"Error applying changes: {e}")
            return False

    def rollback_last_commit(self) -> bool:
        """
        Rollback the last commit.
        """
        try:
            subprocess.check_call(['git', 'reset', '--hard', 'HEAD~1'])
            logger.info("Rollback successful: Last commit reverted.")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = CodeAnalyzer()
    suggestions = analyzer.analyze_codebase()
    logger.info(f"Improvement Suggestions: {suggestions}")
