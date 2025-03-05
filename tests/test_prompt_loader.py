"""
Unit tests for the PromptLoader class.
"""
import os
import unittest
import tempfile
from cherry.prompts.prompt_loader import PromptLoader, create_code_generation_prompt

class TestPromptLoader(unittest.TestCase):
    """Test cases for the PromptLoader class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test templates
        self.temp_dir = tempfile.mkdtemp()
        self.loader = PromptLoader(self.temp_dir)
        
        # Create a test template file
        self.template_content = "Hello {{name}}! Your age is {{age}}."
        self.template_path = os.path.join(self.temp_dir, "test_template.md")
        with open(self.template_path, 'w') as f:
            f.write(self.template_content)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        if os.path.exists(self.template_path):
            os.remove(self.template_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_load_template(self):
        """Test loading a template from file."""
        content = self.loader.load_template("test_template")
        self.assertEqual(content, self.template_content)
        
        # Test with .md extension included
        content = self.loader.load_template("test_template.md")
        self.assertEqual(content, self.template_content)
        
        # Test with non-existent template
        with self.assertRaises(FileNotFoundError):
            self.loader.load_template("non_existent_template")
    
    def test_populate_template(self):
        """Test populating a template with variables."""
        variables = {
            "name": "John",
            "age": 30
        }
        expected = "Hello John! Your age is 30."
        
        result = self.loader.populate_template(self.template_content, variables)
        self.assertEqual(result, expected)
        
        # Test with None value
        variables["age"] = None
        expected = "Hello John! Your age is ."
        result = self.loader.populate_template(self.template_content, variables)
        self.assertEqual(result, expected)
    
    def test_load_and_populate(self):
        """Test loading and populating a template."""
        variables = {
            "name": "Jane",
            "age": 25
        }
        expected = "Hello Jane! Your age is 25."
        
        result = self.loader.load_and_populate("test_template", variables)
        self.assertEqual(result, expected)


class TestCodeGenerationPrompt(unittest.TestCase):
    """Test cases for the create_code_generation_prompt function."""
    
    def test_create_code_generation_prompt(self):
        """Test creating a code generation prompt."""
        # This test assumes the code_generation_prompt.md template exists in the package directory
        # We'll check that the function runs and returns a string containing expected elements
        
        prompt = create_code_generation_prompt(
            description="Test description",
            language="Python",
            requirements=["Req 1", "Req 2"],
            framework="Flask",
            additional_context="Extra info"
        )
        
        # Check that the result is a string
        self.assertIsInstance(prompt, str)
        
        # Check that our inputs are reflected in the output
        self.assertIn("Test description", prompt)
        self.assertIn("Python", prompt)
        self.assertIn("Req 1", prompt)
        self.assertIn("Req 2", prompt)
        self.assertIn("Flask", prompt)
        self.assertIn("Extra info", prompt)


if __name__ == '__main__':
    unittest.main()
