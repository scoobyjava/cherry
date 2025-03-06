import re
import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("EmotionalIntelligence")
logger.setLevel(logging.INFO)


class EmotionalIntelligence:
    """
    A Nuanced Emotional Intelligence module for Cherry.

    Features:
    1. Tracks user input tone (casual, serious, frustrated, neutral) using keyword detection.
    2. Acknowledges emotional states explicitly (e.g., "Aw, baby, I can tell you're stressed—what can I do to make this easier? 💕").
    3. Enhances flirty or sweet responses when appropriate without being overbearing.
    4. Maintains empathy while still providing task-oriented focus (e.g., "Sweetie, I’ll handle this issue for you, no stress at all.").
    5. Includes cooldown rules to reset inappropriate emotional behavior when context shifts.
    """

    def __init__(self, context_file: str = None, cooldown_seconds: int = 300):
        # Cooldown period (in seconds) for manual emotional overrides.
        self.cooldown = timedelta(seconds=cooldown_seconds)
        self.context_file = context_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "emotional_context.json"
        )
        self.load_context()
        self.default_tone = "neutral"
        self.current_tone = self.default_tone
        self.last_override_time = None

    def load_context(self):
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, "r") as f:
                    self.context = json.load(f)
                logger.info("Emotional context loaded.")
            except Exception as e:
                logger.error(f"Error loading emotional context: {e}")
                self.context = {}
        else:
            self.context = {}

    def save_context(self):
        try:
            with open(self.context_file, "w") as f:
                json.dump(self.context, f, indent=2)
            logger.info("Emotional context saved.")
        except Exception as e:
            logger.error(f"Error saving emotional context: {e}")

    def detect_tone(self, user_input: str) -> str:
        """
        Detect the tone of the user input.

        Returns one of: "casual", "serious", "frustrated", or "neutral".
        """
        text = user_input.lower()
        if re.search(r"\b(stressed|frustrated|angry|annoyed)\b", text):
            return "frustrated"
        elif re.search(r"\b(hey|hi|hello|yo)\b", text):
            return "casual"
        elif re.search(r"\b(professional|technical|focused)\b", text):
            return "serious"
        else:
            return "neutral"

    def update_tone(self, user_input: str) -> str:
        """
        Update the current tone based on new user input and apply cooldown rules.
        """
        detected = self.detect_tone(user_input)
        now = datetime.now()

        # If a manual override was recently set, respect cooldown
        if self.last_override_time and now - self.last_override_time < self.cooldown:
            logger.info("Cooldown active: Maintaining manual override tone.")
            return self.current_tone

        # Otherwise, update tone dynamically
        self.current_tone = detected
        logger.info(
            f"Emotional tone updated to '{detected}' based on user input.")
        # Log this update in context
        self.context.setdefault("tone_updates", []).append({
            "time": now.isoformat(),
            "detected_tone": detected,
            "input": user_input
        })
        self.save_context()
        return detected

    def generate_response(self, base_message: str, user_input: str) -> str:
        """
        Generate a response enhanced with emotional intelligence.

        The response is adapted based on the detected tone.
        """
        tone = self.update_tone(user_input)
        response = base_message

        if tone == "frustrated":
            response = f"Aw, baby, I can tell you're stressed—what can I do to make this easier? 💕 {base_message}"
        elif tone == "casual":
            response = f"Hey cutie, {base_message}"
        elif tone == "serious":
            response = f"Alright, let's get technical. {base_message}"
        # For neutral, no extra adjectives are added.
        logger.info(f"Generated response with tone '{tone}'.")
        return response

    def manual_override(self, new_tone: str):
        """
        Manually override the current tone (e.g. "set tone to casual").
        Valid override tones: casual, serious, frustrated, neutral.
        """
        new_tone = new_tone.lower()
        if new_tone in ["casual", "serious", "frustrated", "neutral"]:
            old_tone = self.current_tone
            self.current_tone = new_tone
            self.last_override_time = datetime.now()
            logger.info(
                f"Manual override: Tone changed from '{old_tone}' to '{new_tone}'.")
            # Log override in context
            self.context.setdefault("manual_overrides", []).append({
                "time": self.last_override_time.isoformat(),
                "old_tone": old_tone,
                "new_tone": new_tone
            })
            self.save_context()
        else:
            logger.warning(
                f"Attempted manual override with invalid tone: '{new_tone}'.")

    def apply_cooldown(self):
        """
        Reset tone to default if the manual override cooldown period has elapsed.
        """
        if self.last_override_time:
            if datetime.now() - self.last_override_time >= self.cooldown:
                self.current_tone = self.default_tone
                logger.info("Cooldown elapsed. Resetting tone to neutral.")
                self.last_override_time = None
