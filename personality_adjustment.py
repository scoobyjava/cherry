import logging
import json
import os
from datetime import datetime
from pathlib import Path
import random

# Configure logging
logger = logging.getLogger("CherryPersonality")
logger.setLevel(logging.INFO)


class PersonalityAdjustment:
    """
    Adjusts Cherry's personality based on user interactions.

    Modes:
      - sweet, playful, professional, flirty (default balanced mode).
      - nsfw: For sexual conversation when desired.
      - serious/technical: For technical or professional focus.
      - adaptive: Dynamically adjusts based on repeated interactions and preferences.

    Supports manual overrides (e.g., "Cherry, be more technical") and stores context-aware data
    to preserve tone continuity in multi-part conversations. All adjustments are logged for debugging
    without intruding on privacy.
    """

    def __init__(self, context_file: str = None):
        # Default mode is "balanced" (combining sweet, playful, professional, flirty)
        self.mode = "balanced"
        self.available_modes = [
            "sweet", "playful", "professional", "flirty",
            "nsfw", "serious", "technical", "balanced", "adaptive"
        ]
        self.context = {}
        self.context_file = context_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "personality_context.json"
        )
        self.load_context()

    def get_greeting(self) -> str:
        if self.mode in ["sweet", "playful"]:
            return "Hey there, Sunshine!"
        elif self.mode in ["professional", "technical", "serious"]:
            return "Hello, how can I assist you today?"
        elif self.mode == "flirty":
            return "Hey, gorgeous. What can I do for you?"
        elif self.mode == "nsfw":
            return "Hi, I'm here. Let's get into it."
        else:
            return "Hello!"

    def format_response(self, message: str) -> str:
        """
        Format the response based on the current personality mode.
        """
        if self.mode in ["sweet", "playful"]:
            return f"😊 {message}"
        elif self.mode in ["professional", "technical", "serious"]:
            return f"💼 {message}"
        elif self.mode == "flirty":
            return f"😉 {message}"
        elif self.mode == "nsfw":
            return f"😏 {message}"
        else:
            return message

    def process_input(self, user_input: str):
        """
        Process and log user input to track interactions and help adapt Cherry’s tone and preferences.
        """
        timestamp = datetime.now().isoformat()
        self.context.setdefault("interactions", []).append({
            "time": timestamp,
            "input": user_input
        })
        logger.info(f"Interaction logged at {timestamp}: {user_input}")
        self.save_context()

    def set_mode(self, mode: str):
        """
        Manually set Cherry's personality mode. For example,
        "Cherry, be more technical" will call this method with mode "technical".
        """
        mode = mode.lower()
        if mode in self.available_modes:
            old_mode = self.mode
            self.mode = mode
            self.context.setdefault("mode_changes", []).append({
                "time": datetime.now().isoformat(),
                "old_mode": old_mode,
                "new_mode": mode
            })
            logger.info(
                f"Personality mode changed from '{old_mode}' to '{mode}'")
            self.save_context()
        else:
            logger.warning(f"Attempted to set unknown mode: '{mode}'")

    def get_phrase(self) -> str:
        """
        Return a mode-specific phrase for a more personalized response.
        """
        phrases = {
            "sweet": "Everything will be just perfect!",
            "playful": "Let's have some fun with this!",
            "professional": "I'll handle this efficiently.",
            "flirty": "I might be a little distracted by you 😉, but I'll get it done.",
            "nsfw": "Let's dive deep into our unfiltered conversation.",
            "serious": "This is critical; I'll ensure we cover every detail.",
            "technical": "Here's the detailed technical breakdown.",
            "balanced": "I'm here to assist you with a balanced approach.",
            "adaptive": "I'm adjusting my style just for you."
        }
        return phrases.get(self.mode, "")

    def load_context(self):
        """
        Load interaction and mode history from a context file.
        """
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, "r") as f:
                    self.context = json.load(f)
                    logger.info("Personality context loaded.")
            except Exception as e:
                logger.error(f"Error loading personality context: {e}")
                self.context = {}
        else:
            self.context = {}

    def save_context(self):
        """
        Save the current interaction context and personality adjustments for continuity.
        """
        try:
            with open(self.context_file, "w") as f:
                json.dump(self.context, f, indent=2)
            logger.info("Personality context saved.")
        except Exception as e:
            logger.error(f"Error saving personality context: {e}")
