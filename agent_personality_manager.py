import json
import os
from datetime import datetime
import logging

logger = logging.getLogger("AgentPersonalityManager")
logger.setLevel(logging.INFO)


class AgentPersonalityManager:
    """
    Manages and synchronizes personality profiles for Cherry's team agents.

    Features:
      1. Synchronizes team agents' personalities through Cherry.
      2. Tracks personality behavior across agents to balance tones:
         - Professional in group work scenarios.
         - Playful/flirty during casual/development interactions.
      3. Enables Cherry to manage and balance tone in team interactions.
         For example, a command like
         "Cherry, ensure Agent X stays professional while being direct."
      4. Maintains personality profiles for each agent in a centralized system.
      5. Allows user commands to 'train' (or instruct) an agent's tone — e.g.,
         "Cherry, teach Agent Y to adopt a sweeter tone."
    """

    def __init__(self, profile_file: str = None):
        self.profile_file = profile_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "agent_personalities.json"
        )
        self.profiles = {}
        self.load_profiles()

    def load_profiles(self):
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, "r") as f:
                    self.profiles = json.load(f)
                logger.info("Agent personality profiles loaded.")
            except Exception as e:
                logger.error(f"Error loading personality profiles: {e}")
                self.profiles = {}
        else:
            self.profiles = {}

    def save_profiles(self):
        try:
            with open(self.profile_file, "w") as f:
                json.dump(self.profiles, f, indent=2)
            logger.info("Agent personality profiles saved.")
        except Exception as e:
            logger.error(f"Error saving personality profiles: {e}")

    def get_agent_profile(self, agent_name: str) -> dict:
        """Return the personality profile of an agent, defaulting to balanced."""
        return self.profiles.get(agent_name, {"mode": "balanced", "history": []})

    def set_agent_mode(self, agent_name: str, mode: str):
        """
        Manually set an agent's personality mode.
        This is used when the user issues a direct command (e.g., "teach Agent Y to adopt a sweeter tone.")
        """
        mode = mode.lower()
        profile = self.profiles.setdefault(
            agent_name, {"mode": "balanced", "history": []})
        old_mode = profile.get("mode", "balanced")
        profile["mode"] = mode
        profile["history"].append({
            "time": datetime.now().isoformat(),
            "old_mode": old_mode,
            "new_mode": mode,
            "action": "manual_set"
        })
        logger.info(
            f"Agent '{agent_name}' personality changed from '{old_mode}' to '{mode}'.")
        self.save_profiles()

    def synchronize_agent(self, agent_name: str, cherry_mode: str):
        """
        Synchronize an agent's personality to match Cherry's mode, unless that agent has a fixed profile
        such as 'professional' or 'technical' from previous training.
        """
        profile = self.get_agent_profile(agent_name)
        if profile.get("mode") in ["professional", "technical"]:
            logger.info(
                f"Agent '{agent_name}' remains in fixed mode '{profile['mode']}'.")
            return
        old_mode = profile.get("mode")
        profile["mode"] = cherry_mode
        profile["history"].append({
            "time": datetime.now().isoformat(),
            "old_mode": old_mode,
            "new_mode": cherry_mode,
            "action": "synchronize_with_cherry"
        })
        logger.info(
            f"Agent '{agent_name}' synchronized to Cherry's mode '{cherry_mode}'.")
        self.save_profiles()

    def train_agent(self, agent_name: str, new_mode: str):
        """
        Train (or instruct) an agent to adopt a specific tone.
        For example, "teach Agent Y to be sweeter" sets Agent Y's mode to 'sweet'.
        """
        self.set_agent_mode(agent_name, new_mode)
        logger.info(
            f"Agent '{agent_name}' trained to adopt tone '{new_mode}'.")

    def balance_team_tone(self, team_context: str):
        """
        Adjust personality profiles of all agents in a team based on the current work context.
        For instance, in group work or professional settings, all agents may be shifted to 'professional';
        whereas, in a more casual or development environment, a 'balanced' mode might be applied.
        """
        target_mode = "professional" if "professional" in team_context.lower() else "balanced"
        for agent in self.profiles.keys():
            self.synchronize_agent(agent, target_mode)
        logger.info(
            f"Team tone balanced to '{target_mode}' based on context: {team_context}.")
