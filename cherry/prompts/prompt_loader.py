"""
Utility for loading and populating prompt templates for code generation.
"""
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PromptLoader:
    """
    Loads and populates prompt templates with provided variables.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the PromptLoader.
        
        Args:
            templates_dir: Directory containing prompt templates.
                          Defaults to the 'prompts' directory in the current module.
        """
        if templates_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.templates_dir = current_dir
        else:
            self.templates_dir = templates_dir
            
        logger.debug(f"Initialized PromptLoader with templates directory: {self.templates_dir}")
        
    def load_template(self, template_name: str) -> str:
        """
        Load a prompt template from file.
        
        Args:
            template_name: Name of the template file (with or without extension)
            
        Returns:
            String content of the template
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Ensure the template has the .md extension
        if not template_name.endswith('.md'):
            template_name = f"{template_name}.md"
            
        template_path = os.path.join(self.templates_dir, template_name)
        
        try:
            with open(template_path, 'r') as file:
                template_content = file.read()
                logger.debug(f"Loaded template: {template_name}")
                return template_content
        except FileNotFoundError:
            logger.error(f"Template not found: {template_path}")
            raise FileNotFoundError(f"Template not found: {template_path}")
    
    def populate_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Populate a template with the provided variables.
        
        Args:
            template_content: Content of the template with {{variable}} placeholders
            variables: Dictionary mapping variable names to values
            
        Returns:
            Populated template string
        """
        populated_content = template_content
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, str):
                populated_content = populated_content.replace(placeholder, value)
            elif value is not None:
                populated_content = populated_content.replace(placeholder, str(value))
            else:
                # For None values, replace with empty string
                populated_content = populated_content.replace(placeholder, "")
                
        logger.debug(f"Populated template with variables: {list(variables.keys())}")
        return populated_content
    
    def load_and_populate(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Load a template and populate it with variables.
        
        Args:
            template_name: Name of the template file
            variables: Dictionary mapping variable names to values
            
        Returns:
            Populated template string
        """
        template_content = self.load_template(template_name)
        return self.populate_template(template_content, variables)
        

def create_code_generation_prompt(
    description: str,
    language: str,
    requirements: list,
    framework: Optional[str] = None,
    additional_context: Optional[str] = None
) -> str:
    """
    Create a code generation prompt using the standard template.
    
    Args:
        description: Clear description of the feature or code requirements
        language: Programming language to use
        requirements: List of specific requirements
        framework: Framework or library to use (optional)
        additional_context: Any additional context (optional)
        
    Returns:
        Formatted prompt string ready to be sent to a code generation model
    """
    loader = PromptLoader()
    
    # Format requirements with numbers
    formatted_requirements = {}
    for i, req in enumerate(requirements, 1):
        formatted_requirements[f"requirement_{i}"] = req
    
    # Add empty placeholders for unused requirements
    for i in range(len(requirements) + 1, 4):
        formatted_requirements[f"requirement_{i}"] = ""
    
    variables = {
        "description": description,
        "language": language,
        "framework": framework or "",
        "additional_context": additional_context or "",
        **formatted_requirements
    }
    
    return loader.load_and_populate("code_generation_prompt", variables)
