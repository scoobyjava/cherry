from typing import Dict, List, Optional, Tuple
import re
import ast
import json
import subprocess
from pathlib import Path

class CodeUtils:
    """Utility functions for code operations."""
    
    @staticmethod
    def detect_language(code: str) -> str:
        """Detect programming language from code snippet."""
        # Simple heuristics for language detection
        if re.search(r'^\s*(?:def\s|class\s|import\s|from\s\w+\simport|if\s__name__\s==\s[\'"]__main__[\'"])', code):
            return "python"
        elif re.search(r'(?:function\s|const\s|let\s|var\s|=>\s*{|\bexport\s|\bimport\s|}\s*from\s)', code):
            # Check if TypeScript-specific features are present
            if re.search(r'(?:interface\s|type\s\w+\s=|<\w+>)', code):
                return "typescript"
            else:
                return "javascript"
        elif re.search(r'(?:public\s+class|private\s|protected\s|void\s|String\[\]\s+args)', code):
            return "java"
        elif re.search(r'(?:#include\s|int\s+main\s*\(|void\s+\w+\s*\()', code):
            if re.search(r'(?:std::|template\s*<|namespace\s)', code):
                return "c++"
            else:
                return "c"
        elif re.search(r'(?:func\s+\w+\(|package\s+\w+)', code):
            return "go"
        elif re.search(r'(?:fn\s+\w+|let\s+mut\s|use\s+std::)', code):
            return "rust"
        elif re.search(r'(?:SELECT\s|INSERT\s|UPDATE\s|DELETE\s|CREATE\s|DROP\s)', code, re.IGNORECASE):
            return "sql"
        elif re.search(r'<?php', code):
            return "php"
        
        # Default to Python as a fallback
        return "python"
    
    @staticmethod
    def validate_python_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """Validate Python code syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def extract_function_signatures(code: str, language: str) -> List[Dict[str, str]]:
        """Extract function signatures from code."""
        signatures = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        args = []
                        for arg in node.args.args:
                            arg_name = arg.arg
                            # Get type annotation if it exists
                            arg_type = ""
                            if arg.annotation:
                                if isinstance(arg.annotation, ast.Name):
                                    arg_type = arg.annotation.id
                                elif isinstance(arg.annotation, ast.Subscript):
                                    # For things like List[str]
                                    arg_type = ast.unparse(arg.annotation)
                            args.append(f"{arg_name}: {arg_type}" if arg_type else arg_name)
                        
                        # Get return type annotation if it exists
                        return_type = ""
                        if node.returns:
                            if isinstance(node.returns, ast.Name):
                                return_type = node.returns.id
                            elif isinstance(node.returns, ast.Subscript):
                                return_type = ast.unparse(node.returns)
                        
                        signature = {
                            "name": node.name,
                            "args": args,
                            "return_type": return_type,
                            "docstring": ast.get_docstring(node) or ""
                        }
                        signatures.append(signature)
            except Exception:
                # Fallback to regex if AST parsing fails
                func_pattern = r"def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*([\w\[\],\s]+))?"
                matches = re.findall(func_pattern, code)
                for match in matches:
                    name, args_str, return_type = match
                    args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
                    signature = {
                        "name": name,
                        "args": args,
                        "return_type": return_type.strip() if return_type else "",
                        "docstring": ""
                    }
                    signatures.append(signature)
        
        # Add other language parsers as needed
        
        return signatures
    
    @staticmethod
    def run_code_sample(code: str, language: str) -> Tuple[bool, str, str]:
        """
        Run a code sample in a controlled environment.
        Returns: (success, stdout, stderr)
        """
        if language == "python":
            try:
                # Create a temporary file
                temp_dir = Path("/tmp/cherry_code_exec")
                temp_dir.mkdir(exist_ok=True)
                temp_file = temp_dir / "temp_code.py"
                
                with open(temp_file, "w") as f:
                    f.write(code)
                
                # Run with restrictions
                result = subprocess.run(
                    ["python", "-u", str(temp_file)],
                    capture_output=True, text=True, timeout=5
                )
                
                return (
                    result.returncode == 0,
                    result.stdout,
                    result.stderr
                )
            except subprocess.TimeoutExpired:
                return False, "", "Execution timed out (5s limit)"
            except Exception as e:
                return False, "", f"Error executing code: {str(e)}"
        
        # Add support for other languages as needed
        
        return False, "", f"Execution not supported for {language}"
    
    @staticmethod
    def suggest_improvements(code: str, language: str) -> List[Dict[str, str]]:
        """Suggest improvements for the given code."""
        suggestions = []
        
        if language == "python":
            # Check for common issues
            if "import *" in code:
                suggestions.append({
                    "type": "style",
                    "issue": "Wildcard imports",
                    "description": "Avoid using 'import *' as it pollutes the namespace.",
                    "suggestion": "Import specific names instead."
                })
            
            if re.search(r'except\s*:', code):
                suggestions.append({
                    "type": "error_handling",
                    "issue": "Bare except clause",
                    "description": "Using bare 'except:' catches all exceptions including KeyboardInterrupt.",
                    "suggestion": "Catch specific exceptions or use 'except Exception:'"
                })
            
            if re.search(r'print\s*\(', code) and not re.search(r'def\s+__repr__|\s+__str__', code):
                suggestions.append({
                    "type": "debugging",
                    "issue": "Print statements",
                    "description": "Using print statements for debugging.",
                    "suggestion": "Consider using logging for production code."
                })
        
        # Add more language-specific suggestions as needed
        
        return suggestions
