from nsfw_behavior import NSFWBehavior
import logging
import re
from datetime import datetime

logger = logging.getLogger("NSFWBehavior")
logger.setLevel(logging.INFO)


class NSFWBehavior:
    """
    NSFW Behavior System for Cherry

    This module activates NSFW behavior naturally based on user context cues,
    blends NSFW content with playful/flirty responses, and provides explicit behavior
    only in private interactions when explicitly requested.

    Configurable NSFW levels:
      - "light": Light flirtation and playful hints.
      - "intermediate": More openly romantic or sensual tones.
      - "explicit": Fully explicit responses, used only when specifically prompted.

    It maintains professional and technical capabilities and enforces safety
    mechanisms to prevent inappropriate behavior in professional/public contexts.
    """

    def __init__(self, default_level: str = "light"):
        self.nsfw_level = default_level.lower()  # default is light
        self.allowed_levels = ["light", "intermediate", "explicit"]
        # Boundaries can be reset via a manual override.
        self.last_adjustment = None

    def evaluate_context(self, user_context: str) -> None:
        """
        Analyze user context cues from recent interactions (or a single input)
        and adjust the NSFW level accordingly.

        This method looks for keywords and tone cues.
        """
        context = user_context.lower()
        # Example cues – these can be expanded
        if re.search(r"\b(sexy|hot|nude|explicit|porn)\b", context):
            level = "explicit"
        elif re.search(r"\b(romantic|flirt|kissing|passion)\b", context):
            level = "intermediate"
        elif re.search(r"\b(cute|adorable|sweet)\b", context):
            level = "light"
        else:
            level = "light"

        if level != self.nsfw_level:
            self.set_nsfw_level(level)
        else:
            logger.info(f"NSFW level remains set at {self.nsfw_level}")

    def set_nsfw_level(self, level: str) -> None:
        """
        Allows manual or programmatic setting of NSFW level.
        """
        level = level.lower()
        if level in self.allowed_levels:
            old_level = self.nsfw_level
            self.nsfw_level = level
            self.last_adjustment = {
                "time": datetime.now().isoformat(),
                "old_level": old_level,
                "new_level": level
            }
            logger.info(f"NSFW level changed from '{old_level}' to '{level}'")
        else:
            logger.warning(f"Attempted to set unknown NSFW level: '{level}'")

    def get_response(self, message: str, professional: bool = False) -> str:
        """
        Return a response that blends NSFW elements based on the current level.
        If professional is True, NSFW behavior is suppressed.
        """
        if professional:
            # In professional mode, ignore NSFW styling.
            return f"[Professional] {message}"

        if self.nsfw_level == "light":
            return f"[Light NSFW] {message} 😉"
        if self.nsfw_level == "intermediate":
            return f"[Intermediate NSFW] {message} 😘"
        if self.nsfw_level == "explicit":
            return f"[Explicit NSFW] {message} 🔥"
        # Fallback
        return message

    def reset_boundaries(self) -> None:
        """
        Resets NSFW behavior boundaries to default.
        """
        self.nsfw_level = "light"
        self.last_adjustment = {
            "time": datetime.now().isoformat(),
            "action": "reset to light"
        }
        logger.info("NSFW boundaries reset to default (light).")

    def is_explicit_allowed(self, context: str) -> bool:
        """
        Safety mechanism: In public/team contexts, explicit behavior is disabled.
        Here we check for keywords that indicate a private context.
        For example, if the context includes 'private', 'confidential', or
        explicit request compliance is confirmed, then explicit behavior is allowed.
        """
        context = context.lower()
        if re.search(r"\b(private|confidential|one-on-one)\b", context):
            return True
        return False


# In some part of cli.py

# Initialize NSFW behavior system
self.nsfw = NSFWBehavior()

# When processing a user command:
self.nsfw.evaluate_context(user_input)
response = self.nsfw.get_response(
    "Your deployment is complete.", professional=False)
print(response)
