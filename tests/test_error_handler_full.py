"""
Extended unit tests for the error_handler module.
"""

import unittest
import sys
from src.utils.error_handler import capture_error, analyze_and_fix

class TestErrorHandlerFull(unittest.TestCase):
    def test_index_error_fix(self):
        task_id = "test_task_indexError"
        error_message = "list index out of range (IndexError)"
        # Simulate analysis of the error message.
        fixed_code = analyze_and_fix(task_id, error_message)
        # The fix suggestion should include the safe_access function.
        self.assertIn("def safe_access", fixed_code)
        self.assertIn("except IndexError", fixed_code)
    
    def test_key_error_fix(self):
        task_id = "test_task_keyError"
        error_message = "'missing_key' (KeyError)"
        # Simulate analysis of the error message.
        fixed_code = analyze_and_fix(task_id, error_message)
        # The fix suggestion should include safe dictionary access.
        self.assertIn("dictionary.get", fixed_code)
    
    def test_type_error_fix(self):
        task_id = "test_task_typeError"
        error_message = "'NoneType' object is not callable (TypeError)"
        # Simulate analysis of the error message.
        fixed_code = analyze_and_fix(task_id, error_message)
        # The fix suggestion should include type checking.
        self.assertIn("callable", fixed_code)
    
    def test_real_error_capture(self):
        task_id = "test_real_error"
        try:
            # Trigger a real IndexError
            my_list = [1, 2, 3]
            value = my_list[10]  # This will raise an IndexError
        except Exception as e:
            error_info = capture_error(task_id, e)
            self.assertEqual(error_info['error_type'], 'IndexError')
            self.assertEqual(error_info['task_id'], task_id)
            self.assertTrue('stack_trace' in error_info)

if __name__ == '__main__':
    unittest.main()
