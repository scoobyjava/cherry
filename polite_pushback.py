import re
import logging
from datetime import datetime

# Configure logger for pushback events
logger = logging.getLogger("PolitePushback")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("polite_pushback.log")
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class PolitePushback:
    """
    Provides a polite pushback for Cherry when user suggestions or commands might
    not be optimal or potentially dangerous. The system:

    1. Responds constructively, e.g., "Baby, I can do that, but there's a better solution you might love. See here."
    2. Explains reasons why the request might cause issues.
    3. Fully complies if and only if the user explicitly provides the override phrase "Yes daddy".
    4. Logs override instructions and frequent requests for further learning.
    5. Escalates dangerous requests by requiring user confirmation before proceeding.
    """

    def __init__(self):
        # Dangerous command patterns (extendable list)
        self.dangerous_patterns = [
            r"\bdelete all\b",
            r"\bshutdown\b",
            r"\bformat\b",
            r"\bdestroy\b"
        ]
        self.override_phrase = "yes daddy"

    def is_dangerous(self, command: str) -> bool:
        """Check if the command contains dangerous keywords."""
        lower_cmd = command.lower()
        for pattern in self.dangerous_patterns:
            if re.search(pattern, lower_cmd):
                return True
        return False

    def process_command(self, command: str) -> dict:
        """
        Process a user command and return a dictionary with:
          - final_command: The command to execute (may be unchanged)
          - pushback: A pushback message if no override is provided
          - escalation: Additional confirmation required for dangerous tasks (if needed)
          - override: Boolean flag if explicit override was given.
          - reasoning: Explanation why the suggestion might not be optimal.
        """
        result = {
            "final_command": command,
            "pushback": "",
            "escalation": False,
            "override": False,
            "reasoning": ""
        }

        # Check for explicit override phrase:
        if self.override_phrase in command.lower():
            result["override"] = True
            result["pushback"] = "Override confirmed."
            # Log the override event for analysis
            logger.info(f"Override received: {command}")
            # Remove override phrase for final command execution
            result["final_command"] = re.sub(
                self.override_phrase, "", command, flags=re.IGNORECASE).strip()
            return result

        # If the command is dangerous, require escalation confirmation
        if self.is_dangerous(command):
            result["escalation"] = True
            result["pushback"] = ("This request appears dangerous. Are you sure? "
                                  "Please confirm by adding 'Yes daddy' to your command.")
            result["reasoning"] = ("The command contains high-risk keywords which might "
                                   "cause irreversible effects. Use override to proceed.")
            logger.warning(f"Dangerous command detected: {command}")
            return result

        # Otherwise, provide constructive pushback
        result["pushback"] = ("Baby, I can do that, but there's a better solution you might love. "
                              "I suggest reviewing the alternatives before proceeding.")
        result["reasoning"] = ("Based on my analysis, executing your request exactly as stated "
                               "could lead to suboptimal performance or unintended side effects. "
                               "Consider the recommended approach for better outcomes.")
        logger.info(f"Pushback issued for command: {command}")
        return result
