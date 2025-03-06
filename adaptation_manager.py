import json
import os
from datetime import datetime
import logging

logger = logging.getLogger("AdaptationManager")
logger.setLevel(logging.INFO)


def load_json(filepath: str, default):
    """
    A common JSON loader that returns a default value if file does not exist
    or if an error occurs. This ensures a consistent data type.
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            # Ensure data is of expected type
            if isinstance(default, dict) and not isinstance(data, dict):
                return default
            if isinstance(default, list) and not isinstance(data, list):
                return default
            return data
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return default
    return default


class AdaptationManager:
    """
    Aggregates logs and preference data from Cherry's personality, NSFW, and endearment systems.

    Features:
      1. Tracks user personality and NSFW preference changes to improve responses over time.
      2. Analyzes feedback loops (e.g., summary of frequently used override commands or adjustments).
      3. Balances personality growth to avoid unwanted biases (ensuring Cherry doesn't become overly technical 
         or too playful unless explicitly requested).
      4. Provides summary insights from these logs to guide future interactions.
    """

    def __init__(self,
                 personality_context_file: str = None,
                 endearment_pref_file: str = None,
                 override_log_file: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.personality_context_file = personality_context_file or os.path.join(
            base_dir, "personality_context.json")
        self.endearment_pref_file = endearment_pref_file or os.path.join(
            base_dir, "endearment_preferences.json")
        # Expect override logs always as a list.
        self.override_log_file = override_log_file or os.path.join(
            base_dir, "nsfw_override_log.json")

    def load_json_log(self, filepath: str, default):
        return load_json(filepath, default)

    def aggregate_feedback(self) -> dict:
        """
        Loads logs and preferences from related modules and aggregates a summary.
        Expected formats:
         - Personality context: a dictionary with key "mode_changes": list.
         - NSFW override events: a list.
         - Endearment preferences: a dictionary.
        """
        summary = {}

        personality_logs = self.load_json_log(
            self.personality_context_file, {"mode_changes": []})
        nsfw_overrides = self.load_json_log(self.override_log_file, [])
        endearment_prefs = self.load_json_log(self.endearment_pref_file, {
                                              "default_term": "sweetie", "frequency": 0.5})

        # Aggregate personality mode changes
        mode_changes = personality_logs.get("mode_changes", [])
        summary["mode_change_count"] = len(mode_changes)
        mode_freq = {}
        if mode_changes:
            for change in mode_changes:
                new_mode = change.get("new_mode", "unknown")
                mode_freq[new_mode] = mode_freq.get(new_mode, 0) + 1
        summary["mode_frequencies"] = mode_freq

        # Aggregate NSFW override events
        summary["nsfw_override_count"] = len(nsfw_overrides)

        # Aggregate endearment preferences (ensure defaults if missing)
        summary["preferred_term"] = endearment_prefs.get(
            "default_term", "sweetie")
        summary["endearment_frequency"] = endearment_prefs.get(
            "frequency", 0.5)

        return summary

    def generate_summary_insight(self) -> str:
        """
        Generates a human-readable summary insight from aggregated logs and preferences.
        """
        feedback = self.aggregate_feedback()
        insights = []

        # Summarize personality changes
        if feedback["mode_change_count"] > 0:
            total = feedback["mode_change_count"]
            if feedback["mode_frequencies"]:
                dominant_mode = max(
                    feedback["mode_frequencies"].items(), key=lambda x: x[1])[0]
            else:
                dominant_mode = "balanced"
            insights.append(
                f"You've adjusted personality modes {total} time(s), favoring a '{dominant_mode}' tone.")
        else:
            insights.append("Personality mode has remained stable.")

        # Summarize NSFW override usage
        if feedback["nsfw_override_count"] > 0:
            insights.append(
                f"You've used explicit override {feedback['nsfw_override_count']} time(s) for NSFW interactions.")
        else:
            insights.append(
                "No explicit NSFW overrides have been used recently.")

        # Summarize endearment preferences
        term = feedback["preferred_term"]
        frequency = feedback["endearment_frequency"]
        if frequency > 0.7:
            insights.append(
                f"Your responses favor a very flirty tone; I'll be calling you '{term}' quite frequently. 💕")
        elif frequency < 0.3:
            insights.append(
                f"It seems you prefer a low-key approach; I'll use '{term}' sparingly.")
        else:
            insights.append(
                f"I see you like a balanced tone with '{term}' used moderately.")

        summary_insight = " ".join(insights)
        logger.info(f"Adaptation summary insight generated: {summary_insight}")
        return summary_insight
