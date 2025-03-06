import re
from typing import Dict, Any, Tuple, List


class NLPProcessor:
    """Simple NLP processor for Cherry CLI that maps natural language to commands"""

    def __init__(self):
        self.intents = {
            "run_simulation": [
                r"run\s+simulation",
                r"start\s+simulation",
                r"simulate",
                r"test\s+in\s+sandbox"
            ],
            "run_staging": [
                r"run\s+staging",
                r"deploy\s+to\s+staging",
                r"test\s+deployment",
                r"stage"
            ],
            "analyze": [
                r"analyze",
                r"assess",
                r"evaluate",
                r"review\s+results",
                r"suggest\s+improvements"
            ],
            "self_test": [
                r"self\s+test",
                r"test\s+yourself",
                r"run\s+self\s+analysis",
                r"evaluate\s+your\s+performance"
            ],
            "create_test": [
                r"create\s+test",
                r"new\s+test",
                r"make\s+test\s+case",
                r"define\s+test"
            ],
            "show_history": [
                r"(show|display)\s+history",
                r"command\s+history",
                r"previous\s+commands",
                r"past\s+runs"
            ],
            "show_reports": [
                r"(show|list)\s+reports",
                r"available\s+reports",
                r"report\s+list",
                r"find\s+reports"
            ],
            "help": [
                r"help",
                r"commands",
                r"what\s+can\s+you\s+do",
                r"available\s+options",
                r"how\s+to\s+use"
            ],
            "exit": [
                r"exit",
                r"quit",
                r"stop",
                r"bye",
                r"end"
            ]
        }

    def process_input(self, user_input: str) -> Tuple[str, float]:
        """
        Process natural language input and map to command
        Returns: (command, confidence)
        """
        user_input = user_input.lower().strip()
        best_match = None
        best_confidence = 0.0

        # Check direct command match first
        for command in self.intents.keys():
            if user_input == command.replace("_", " "):
                return command, 1.0

        # Check for intent patterns
        for command, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, user_input):
                    # Found a match - calculate confidence based on length ratio
                    match_len = len(pattern)
                    input_len = len(user_input)
                    # Simple confidence metric: how much of input matches our pattern
                    confidence = match_len / input_len if input_len > 0 else 0
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = command

        if best_match and best_confidence > 0.3:  # Threshold for accepting a match
            return best_match, best_confidence
        else:
            return None, 0.0
