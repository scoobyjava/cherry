import logging
from datetime import datetime

logger = logging.getLogger("NSFWOverride")
logger.setLevel(logging.INFO)


class NSFWOverride:
    """
    Provides explicit override functionality for Cherry's NSFW interactions.

    Features:
      1. Logs specific triggers for NSFW conversations only in private contexts.
      2. Acknowledges explicit requests directly while blending them into natural conversations.
      3. Reverts to other tasks effortlessly after explicit interactions to prioritize productivity.
      4. Includes safeguards that allow manual NSFW resets for other users or context changes; for example,
         disabling explicit mode during professional meetings or team interactions.
    """

    def __init__(self):
        self.explicit_mode = False
        self.override_log = []  # List to record explicit override events

    def process_request(self, command: str, context: dict) -> dict:
        """
        Processes an explicit NSFW request.

        If the context is private and the explicit override phrase (e.g., "Yes daddy")
        is present in the command, activate explicit NSFW mode.

        Returns:
          {
            "execute": bool,        # Whether to execute NSFW explicit behavior immediately.
            "message": str,         # Acknowledgement or pushback message.
            "explicit_mode": bool   # Current NSFW explicit mode state.
          }
        """
        result = {
            "execute": False,
            "message": "",
            "explicit_mode": self.explicit_mode
        }

        # Only allow explicit NSFW interactions in private contexts.
        if not context.get("private", False):
            result["message"] = "Explicit NSFW interactions are allowed only in private contexts."
            logger.info(
                "NSFW explicit override request denied: public context.")
            return result

        explicit_trigger = "yes daddy"
        if explicit_trigger in command.lower():
            self.explicit_mode = True
            result["execute"] = True
            result["explicit_mode"] = True
            result["message"] = "Explicit override confirmed. Proceeding with explicit NSFW responses."
            self.log_override(command, context)
        else:
            result["message"] = "NSFW explicit mode is available if you wish—simply say 'Yes daddy'."
            result["execute"] = False
            logger.info(
                "No explicit override trigger detected in the request.")

        return result

    def log_override(self, command: str, context: dict):
        """
        Log the explicit NSFW override request for further analysis.
        """
        log_entry = {
            "time": datetime.now().isoformat(),
            "command": command,
            "context": context,
            "action": "explicit override activated"
        }
        self.override_log.append(log_entry)
        logger.info(f"Logged explicit NSFW override: {log_entry}")

    def reset_explicit_mode(self):
        """
        Resets explicit NSFW mode; this safeguard can be triggered manually when, for example,
        switching to professional tasks or group interactions.
        """
        self.explicit_mode = False
        logger.info("Explicit NSFW mode has been reset to off.")
