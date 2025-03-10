"""
Unit tests for the Cherry AI Agent Collaboration Framework.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging

from src.agents.collaboration import DeveloperAgent, ReviewerAgent


class TestAgentCollaboration(unittest.TestCase):
    """Test cases for the agent collaboration framework."""

    def setUp(self):
        """Set up test fixtures."""
        logging.disable(logging.CRITICAL)
        self.developer = DeveloperAgent("TestDev")
        self.reviewer = ReviewerAgent("TestReviewer")
        self.developer.set_reviewer(self.reviewer)

    def tearDown(self):
        """Clean up after tests."""
        logging.disable(logging.NOTSET)

    def test_developer_generate_code(self):
        """Test that the developer can generate initial code."""
        code = self.developer.generate_code("add two numbers")
        self.assertIn("def add_numbers", code)
        self.assertIn("return a + b", code)

    def test_reviewer_finds_issues(self):
        """Test that the reviewer can find issues in code."""
        code = "def add_numbers(a, b):\n    return a + b"
        feedback, approved = self.reviewer.review(code)
        self.assertFalse(approved)
        self.assertIn("issue", feedback.lower())

    def test_reviewer_approves_good_code(self):
        """Test that the reviewer approves good code."""
        code = (
            "def add_numbers(a, b):\n"
            '    """Add two numbers and return the sum."""\n'
            "    return a + b"
        )
        feedback, approved = self.reviewer.review(code)
        self.assertTrue(approved)
        self.assertIn("approved", feedback.lower())


if __name__ == '__main__':
    unittest.main()
