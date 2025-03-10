"""
Error handling module for Cherry.

This module provides functionality to capture runtime errors from executed code tasks,
analyze them, and suggest fixes automatically.
"""

import logging
import traceback
import sys
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store error records for analysis
error_records = {}

def capture_error(task_id: str, error: Exception) -> Dict[str, Any]:
    """
    Capture runtime errors from executed code tasks.
    
    Args:
        task_id (str): The identifier for the task that raised the error
        error (Exception): The exception that was raised
        
    Returns:
        Dict[str, Any]: A dictionary containing error information
    """
    # Extract stack trace information
    tb = traceback.extract_tb(sys.exc_info()[2])
    stack_frames = []
    
    for frame in tb:
        stack_frames.append({
            'filename': frame.filename,
            'line': frame.line,
            'lineno': frame.lineno,
            'name': frame.name
        })
    
    # Capture error details
    error_info = {
        'task_id': task_id,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'stack_trace': stack_frames,
        'timestamp': datetime.now().isoformat()
    }
    
    # Log the error
    logger.error(f"Task {task_id} failed with {error_info['error_type']}: {error_info['error_message']}")
    logger.debug(f"Stack trace: {stack_frames}")
    
    # Store error record for later analysis
    error_records[task_id] = error_info
    
    return error_info

def analyze_and_fix(task_id: str, error_message: str) -> str:
    """
    Analyze error and suggest fixes based on error patterns.
    
    Args:
        task_id (str): The identifier for the task that raised the error
        error_message (str): The error message to analyze
        
    Returns:
        str: Suggested code fix
    """
    logger.info(f"Analyzing error for task {task_id}: {error_message}")
    
    # Get stored error information if available
    error_info = error_records.get(task_id, {})
    
    # Analyze different error types and suggest fixes
    if "IndexError" in error_message or "list index out of range" in error_message:
        logger.info(f"Detected IndexError in task {task_id}")
        fix = _generate_index_error_fix(error_info)
        logger.info(f"Generated fix for IndexError in task {task_id}")
        return fix
    
    elif "KeyError" in error_message:
        logger.info(f"Detected KeyError in task {task_id}")
        fix = _generate_key_error_fix(error_info)
        logger.info(f"Generated fix for KeyError in task {task_id}")
        return fix
    
    elif "TypeError" in error_message:
        logger.info(f"Detected TypeError in task {task_id}")
        fix = _generate_type_error_fix(error_info)
        logger.info(f"Generated fix for TypeError in task {task_id}")
        return fix
    
    else:
        logger.info(f"No specific fix pattern for error: {error_message}")
        # Generic error handling suggestion
        return _generate_generic_error_fix(error_message)

def _generate_index_error_fix(error_info: Dict[str, Any]) -> str:
    """Generate a fix for IndexError."""
    return """
# Fixed code with safe list access:
def safe_access(lst, index, default=None):
    \"\"\"
    Safely access a list element with an index.
    Returns the element if index is valid, otherwise returns default value.
    \"\"\"
    try:
        return lst[index]
    except IndexError:
        return default

# Example usage:
# Instead of: value = my_list[index]
# Use: value = safe_access(my_list, index)

# This ensures your code doesn't crash when an index is out of range
# You can also provide a default value if needed:
# value = safe_access(my_list, index, default="Not found")
"""

def _generate_key_error_fix(error_info: Dict[str, Any]) -> str:
    """Generate a fix for KeyError."""
    return """
# Fixed code with safe dictionary access:
def safe_dict_access(dictionary, key, default=None):
    \"\"\"
    Safely access a dictionary value using a key.
    Returns the value if key exists, otherwise returns default value.
    \"\"\"
    return dictionary.get(key, default)

# Example usage:
# Instead of: value = my_dict[key]
# Use: value = safe_dict_access(my_dict, key)
# Or simply: value = my_dict.get(key)
"""

def _generate_type_error_fix(error_info: Dict[str, Any]) -> str:
    """Generate a fix for TypeError."""
    return """
# Fixed code with type checking:
def safe_call(function, *args, **kwargs):
    \"\"\"
    Safely call a function with args and kwargs.
    Returns the result if function is callable, otherwise returns None.
    \"\"\"
    if callable(function):
        return function(*args, **kwargs)
    return None

# Example usage:
# Instead of: result = obj.method()
# Use: result = safe_call(getattr(obj, 'method', None))
"""

def _generate_generic_error_fix(error_message: str) -> str:
    """Generate a generic error fix based on the error message."""
    return f"""
# Error analysis for: {error_message}
# Recommended fixes:

# 1. Add proper error handling with try-except blocks:
try:
    # Your code that might raise an exception
    pass
except Exception as e:
    # Handle the exception appropriately
    print(f"An error occurred: {{str(e)}}")
    # Provide a fallback behavior or default value
"""

def simulate_error_scenario():
    """
    Simulate a scenario where Cherry runs a faulty code snippet,
    detects an error, and generates a fix.
    """
    logger.info("Simulating error scenario...")
    
    try:
        # Simulate executing the faulty code
        logger.info("Executing faulty code...")
        sample_list = [1, 2, 3]
        n = 5  # Index out of range
        
        # This will raise an IndexError
        result = sample_list[n]
        
    except Exception as e:
        # Capture the error
        task_id = "demo_task_001"
        error_info = capture_error(task_id, e)
        
        # Analyze and fix
        fixed_code = analyze_and_fix(task_id, str(e))
        
        logger.info("Error detected and fix generated:")
        logger.info(f"Original error: {error_info['error_type']}: {error_info['error_message']}")
        logger.info(f"Generated fix: {fixed_code}")
        
        return {
            "error_info": error_info,
            "fixed_code": fixed_code
        }

if __name__ == "__main__":
    # Run the simulation when executed directly
    simulate_error_scenario()
    print("\nSimulation completed successfully!")
