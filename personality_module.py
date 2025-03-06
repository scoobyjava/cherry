import re
import logging

logger = logging.getLogger("PersonalityModule")
logger.setLevel(logging.INFO)


class PersonalityModule:
    """
    A dedicated personality module for Cherry that overlays responses with the desired tone
    while preserving professional boundaries.

    Features:
      • Adjusts tone of responses using predefined templates (sweet, playful, flirtatious, professional).
      • Incorporates explicit command triggers (e.g., "I'm serious") to activate NSFW responses,
        provided the context (e.g., a private setting) allows.
      • Provides fallback mechanisms for questionable requests to maintain ethical standards.
      • Uses endearing phrases in responses while balancing personality with professional error handling.
    """

    def __init__(self):
        # Default tone is balanced (could be one of: sweet, playful, flirtatious, professional)
        self.current_tone = "balanced"
        # Tone templates for each mode
        self.tone_templates = {
            "sweet": {"prefix": "Dear, ", "suffix": " Sending warm vibes 💕"},
            "playful": {"prefix": "Hey there, ", "suffix": " Let's make it fun! 😉"},
            "flirtatious": {"prefix": "Oh, darling, ", "suffix": " Can't wait to impress you 😘"},
            "professional": {"prefix": "", "suffix": ""},
            "nsfw": {"prefix": "Explicit mode activated: ", "suffix": " 🔥"}
        }
        # Fallback message in cases of questionable requests
        self.fallback_message = ("I'm sorry, but that request appears to be inappropriate. "
                                 "Please rephrase or consider an alternative approach.")

    def set_tone(self, tone: str):
        """
        Set the current tone. Valid tones are keys in self.tone_templates.
        If an unknown tone is specified, fall back to professional.
        """
        tone = tone.lower()
        if tone in self.tone_templates:
            self.current_tone = tone
            logger.info(f"Tone set to '{tone}'.")
        else:
            logger.warning(
                f"Unknown tone '{tone}' specified. Falling back to professional tone.")
            self.current_tone = "professional"

    def is_explicit_triggered(self, command: str) -> bool:
        """
        Returns True if the command includes explicit triggers (e.g., "I'm serious")
        that should activate NSFW responses.
        """
        return bool(re.search(r"\bi'?m serious\b", command, re.IGNORECASE))

    def overlay_response(self, base_message: str, command: str, context: dict = None) -> str:
        """
        Overlays a response with the desired personality tone.

        Parameters:
          • base_message: The main content to be delivered.
          • command: The user command triggering the response.
          • context: Dictionary providing context parameters (e.g., {"private": True, "mode": "professional",
                      "questionable": False}).

        Behavior:
          - Activates NSFW tone if explicit trigger is detected and the context is private.
          - In professional contexts (or when colleagues are involved), it defaults to professional.
          - If context flags a questionable request, returns a fallback message.
        """
        context = context or {}
        # Check if the explicit NSFW trigger is active
        if self.is_explicit_triggered(command) and context.get("private", False):
            chosen_tone = "nsfw"
        else:
            # Check if context indicates a professional setting
            if context.get("mode", "").lower() == "professional" or context.get("colleagues", False):
                chosen_tone = "professional"
            else:
                chosen_tone = self.current_tone

        # Fallback: if the context flags the request as questionable, use fallback message
        if context.get("questionable", False):
            logger.info(
                "Request flagged as questionable. Using fallback response.")
            return self.fallback_message

        template = self.tone_templates.get(
            chosen_tone, self.tone_templates["professional"])
        response = f"{template['prefix']}{base_message}{template['suffix']}"
        logger.info(f"Response overlaid with tone '{chosen_tone}': {response}")
        return response
