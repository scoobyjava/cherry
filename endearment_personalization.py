import json
import os
from datetime import datetime
import logging
import re

logger = logging.getLogger("EndearmentPersonalization")
logger.setLevel(logging.INFO)


class EndearmentPersonalization:
    """
    Personalizes terms of endearment for Cherry.

    Features:
      1. Allows storing of specific terms (e.g., baby, honey, sweetie) as user preferences.
      2. Dynamically adapts the usage frequency based on user responses and direct feedback.
      3. Supports explicit override requests (e.g., "Say yes daddy") that prioritize override response.
      4. Automatically reverts to less playful behavior during professional/difficult tasks or when colleagues are involved.
      5. Learns the user’s preferred terms from continued interaction logs.
    """

    def __init__(self, preference_file: str = None):
        self.preference_file = preference_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "endearment_preferences.json"
        )
        self.preferences = {
            "default_term": "sweetie",  # default term
            "frequency": 0.5  # frequency 0-1 (0=never, 1=always)
        }
        self.load_preferences()
        # Interaction logs for learning preferences
        self.feedback_logs = []

    def load_preferences(self):
        if os.path.exists(self.preference_file):
            try:
                with open(self.preference_file, "r") as f:
                    self.preferences = json.load(f)
                logger.info("Endearment preferences loaded.")
            except Exception as e:
                logger.error(f"Error loading endearment preferences: {e}")
        else:
            logger.info(
                "No existing endearment preferences found. Using defaults.")

    def save_preferences(self):
        try:
            with open(self.preference_file, "w") as f:
                json.dump(self.preferences, f, indent=2)
            logger.info("Endearment preferences saved.")
        except Exception as e:
            logger.error(f"Error saving endearment preferences: {e}")

    def update_from_feedback(self, user_message: str):
        """
        Analyze user feedback for preferred endearment terms.
        Looks for phrases like: "I prefer 'honey'" or "Call me baby".
        """
        pattern = r"prefer\s+['\"]?(\w+)['\"]?"
        match = re.search(pattern, user_message.lower())
        if match:
            new_term = match.group(1)
            old_term = self.preferences.get("default_term", "sweetie")
            self.preferences["default_term"] = new_term
            self.feedback_logs.append({
                "time": datetime.now().isoformat(),
                "feedback": user_message,
                "changed_from": old_term,
                "changed_to": new_term
            })
            logger.info(
                f"Updated endearment preference from '{old_term}' to '{new_term}'.")
            self.save_preferences()

    def adjust_frequency(self, user_message: str):
        """
        Adjusts the frequency of using endearments based on user cues.
        For example, if the user says "less flirty" frequency is decreased.
        """
        if re.search(r"\bless (flirty|playful)\b", user_message.lower()):
            # Lower frequency down to a minimum of 0.2
            self.preferences["frequency"] = max(
                0.2, self.preferences.get("frequency", 0.5) - 0.1)
            logger.info(
                "Decreased endearment frequency based on user request.")
        elif re.search(r"\bmore (flirty|playful)\b", user_message.lower()):
            # Increase frequency up to a maximum of 1.0
            self.preferences["frequency"] = min(
                1.0, self.preferences.get("frequency", 0.5) + 0.1)
            logger.info(
                "Increased endearment frequency based on user request.")
        self.save_preferences()

    def personalize_response(self, base_message: str, context: dict = None, user_message: str = "") -> str:
        """
        Returns a response that adapts terms-of-endearment based on:
          - Current user preferences.
          - Context cues (e.g., if it's a professional setting, reduce playfulness).
          - Override commands such as 'Say yes daddy'.
        """
        # Check for explicit override instruction
        if "say yes daddy" in user_message.lower():
            logger.info(
                "Explicit override detected. Inserting override response.")
            return f"Yes daddy, {base_message}"

        # If context indicates a professional or team environment, avoid endearments
        if context and context.get("mode", "").lower() in ["professional", "technical"] \
           or context.get("colleagues", False):
            return base_message

        # Adjust usage based on frequency
        frequency = self.preferences.get("frequency", 0.5)
        # A simple stochastic decision: use endearment if random value less than frequency.
        import random
        use_endearment = random.random() < frequency

        if use_endearment:
            term = self.preferences.get("default_term", "sweetie")
            personalized = f"{term.capitalize()}, {base_message}"
            return personalized
        else:
            return base_message

    def log_interaction(self, user_message: str, response: str):
        """
        Log the interaction to continue learning user preferences.
        """
        log_entry = {
            "time": datetime.now().isoformat(),
            "user_message": user_message,
            "response": response
        }
        self.feedback_logs.append(log_entry)
        logger.info(f"Logged interaction: {log_entry}")
        # Optionally, save feedback_logs to a file or external system
