"""
Module for AI agent collaboration in Cherry.erry.

Defines DeveloperAgent and ReviewerAgent for pair programming simulation.
"""

import loggingort logging
import timeimport time
from typing import Tuple, Optional, List, Dict, Anyport Tuple, Optional, List, Dict, Any

# Configure logging
logging.basicConfig(logging.basicConfig(
    level=logging.INFO,NFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'e)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cherry.agents")

class AgentInterface:
    """Base interface for all Cherry agents."""    """Base interface for all Cherry agents."""
    
    def __init__(self, name: str):
        """    """
        Initialize an agent.
        
        Args:
            name: Unique identifier for this agent    name: Unique identifier for this agent
        """
        self.name = name
        self.logger = logging.getLogger(f"cherry.agents.{name}")f.logger = logging.getLogger(f"cherry.agents.{name}")
        
    def log_action(self, action: str, details: Any = None):
        """"""
        Log an agent action with optional details.
        
        Args:
            action: Description of the action    action: Description of the action
            details: Additional details about the actionetails: Additional details about the action
        """
        message = f"{self.name}: {action}"
        if details:details:
            if isinstance(details, str) and len(details) > 500:d len(details) > 500:
                # Truncate long code for better logsruncate long code for better logs
                shortened = details[:250] + "..." + details[-250:]0:]
                self.logger.info(f"{message}\n{shortened}")ened}")
            else:
                self.logger.info(f"{message}\n{details}")
        else:
            self.logger.info(message)


class DeveloperAgent(AgentInterface):class DeveloperAgent(AgentInterface):
    """    """
    DeveloperAgent generates code solutions and refines them with feedback from a ReviewerAgent.utions and refines them with feedback from a ReviewerAgent.
    """

    def __init__(self, name: str, reviewer: ReviewerAgent = None):def __init__(self, name: str, reviewer: ReviewerAgent = None):
        """
        Initialize DeveloperAgent.

        Args:    Args:
            name: Identifier for the developer agent.gent.
            reviewer: Optional ReviewerAgent instance.instance.
        """
        self.name = name
        self.reviewer = reviewerself.reviewer = reviewer

    def set_reviewer(self, reviewer: ReviewerAgent):_reviewer(self, reviewer: ReviewerAgent):
        """
        Set the reviewer for the developer.Set the reviewer for the developer.

        Args:
            reviewer: A ReviewerAgent instance. reviewer: A ReviewerAgent instance.
        """
        self.reviewer = reviewerself.reviewer = reviewer

    def generate_code(self, task_description: str) -> str:erate_code(self, task_description: str) -> str:
        """
        Generate an initial code solution based on the task description.Generate an initial code solution based on the task description.

        Args:
            task_description: The task description text.task_description: The task description text.

        Returns:
            A code snippet as a string. A code snippet as a string.
        """
        if "add two numbers" in task_description.lower():
            return (
                "def add_numbers(a, b):\n"        "def add_numbers(a, b):\n"
                "    return a + b"
            )
        return "# Code generation is not implemented for this task." generation is not implemented for this task."

    def collaborate(self, task_description: str) -> str:ate(self, task_description: str) -> str:
        """
        Collaborate with the ReviewerAgent to refine code.borate with the ReviewerAgent to refine code.

        Args:
            task_description: The task description..

        Returns:
            The refined code solution.    The refined code solution.
        """
        if self.reviewer is None:elf.reviewer is None:
            raise ValueError("Reviewer is not set for DeveloperAgent.")eveloperAgent.")
            
        max_iterations = 5max_iterations = 5
        iteration = 0
        code_solution = self.generate_code(task_description)e_solution = self.generate_code(task_description)
        print(f"[Iteration {iteration}] {self.name} initial solution:\n{code_solution}\n")ame} initial solution:\n{code_solution}\n")

        while iteration < max_iterations: iteration < max_iterations:
            feedback, approved = self.reviewer.review(code_solution)iew(code_solution)
            print(f"[Iteration {iteration}] Reviewer feedback: {feedback} | Approved: {approved}")ewer feedback: {feedback} | Approved: {approved}")
            if approved:if approved:
                print(f"[Iteration {iteration}] Final solution accepted.")print(f"[Iteration {iteration}] Final solution accepted.")
                return code_solution
            else: else:
                code_solution = self.revise_code(code_solution, feedback)
                iteration += 1
                print(f"[Iteration {iteration}] Revised solution:\n{code_solution}\n")code_solution}\n")
        print("[Collaboration] Maximum iterations reached. Returning last solution.")print("[Collaboration] Maximum iterations reached. Returning last solution.")
        return code_solution

    def revise_code(self, current_code: str, feedback: str) -> str:: str) -> str:
        """
        Revise the code based on feedback.

        Args::
            current_code: The current code snippet.t.
            feedback: Feedback string from the reviewer.

        Returns:
            Revised code snippet as a string. a string.
        """
        if "docstring" in feedback.lower():
            lines = current_code.splitlines()    lines = current_code.splitlines()
            new_lines = []
            added_docstring = False
            for line in lines:
                new_lines.append(line)
                if not added_docstring and line.strip().startswith("def add_numbers("):ne.strip().startswith("def add_numbers("):
                    # Insert a docstring line
                    indentation = " " * (len(line) - len(line.lstrip()) + 4)   indentation = " " * (len(line) - len(line.lstrip()) + 4)
                    new_lines.append(f'{indentation}"""Add two numbers and return their sum."""')   new_lines.append(f'{indentation}"""Add two numbers and return their sum."""')
                    added_docstring = True= True
            return "\n".join(new_lines)
        # For other feedback types, additional revise logic can be implemented.ditional revise logic can be implemented.
        return current_code


class ReviewerAgent(AgentInterface):
    """
    ReviewerAgent checks code solutions for efficiency, security, and coding standards.ewerAgent checks code solutions for efficiency, security, and coding standards.
    """

    def __init__(self, name: str):
        self.name = name

    def review(self, code: str) -> Tuple[str, bool]:) -> Tuple[str, bool]:
        """
        Review the provided code.

        Args:
            code: The proposed code solution.

        Returns:
            A tuple (feedback, approved) where feedback is a string and approved is a boolean.ple (feedback, approved) where feedback is a string and approved is a boolean.
        """
        feedback = ""
        approved = True

        # Check for the "add_numbers" function and a docstring." function and a docstring.
        if "def add_numbers(" in code:
            lines = code.splitlines()
            for idx, line in enumerate(lines):
                if line.strip().startswith("def add_numbers("):f line.strip().startswith("def add_numbers("):
                    # Check the next few lines for a docstring.       # Check the next few lines for a docstring.
                    next_lines = lines[idx + 1 : idx + 4]
                    if not any(l.strip().startswith('"""') or l.strip().startswith("'''") for l in next_lines):or l in next_lines):
                        feedback += "Docstring is missing – issue: please add a docstring for clarity. "            feedback += "Docstring is missing – issue: please add a docstring for clarity. "
                        approved = False
                    break
        else:else:
            feedback += "Function 'add_numbers' not found – issue: invalid implementation. "entation. "
            approved = False approved = False

        if approved:if approved:
            feedback = "Code approved."
        return feedback, approvedd
