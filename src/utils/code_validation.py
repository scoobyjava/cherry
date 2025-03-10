"""
Utility module for code validation in Cherry.

This module provides functions to enforce Cherry's coding standards
and security checks on Python code snippets.
"""

import re
import subprocess
from typing import List, Dict, Pattern, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Style check patterns
STYLE_PATTERNS: Dict[str, Tuple[Pattern, str]] = {
    "long_line": (
        re.compile(r"^.{80,}$", re.MULTILINE),
        "Line exceeds 79 characters"
    ),
    "todo_comment": (
        re.compile(r"#\s*TODO", re.IGNORECASE),
        "TODO comment found"
    ),
    "trailing_whitespace": (
        re.compile(r"[ \t]+$", re.MULTILINE),
        "Trailing whitespace"
    ),
    "multiple_imports": (
        re.compile(r"import\s+([^,\n]+,\s*)+[^,\n]+"),
        "Multiple imports on one line"
    ),
    "bad_variable_name": (
        re.compile(r"\b[a-z]{1,2}\b\s*="),
        "Variable name too short (use descriptive names)"
    ),
    "inconsistent_indentation": (
        re.compile(r"^( {1,3}|\t+| {5,7})[^ \t\n]", re.MULTILINE),
        "Inconsistent indentation (use 4 spaces)"
    ),
    "missing_docstring": (
        re.compile(r"def\s+\w+\s*\([^)]*\):\s*(?!\s*[\"\']{3})", re.MULTILINE),
        "Function missing docstring"
    ),
    "mutable_default_arg": (
        re.compile(r"def\s+\w+\s*\([^)]*=\s*(\[\]|{}|\(\))[^)]*\)"),
        "Mutable default argument (use None instead)"
    ),
}

# Security check patterns
SECURITY_PATTERNS: Dict[str, Tuple[Pattern, str]] = {
    "exec_eval": (
        re.compile(r"\b(exec|eval)\s*\("),
        "Use of exec() or eval() is a security risk"
    ),
    "shell_injection": (
        re.compile(r"\b(os\.system|os\.popen|subprocess\.call|subprocess\.Popen)\s*\([^)]*(\$|format|f[\"']|\+)"),
        "Potential command injection vulnerability"
    ),
    "sql_injection": (
        re.compile(r"execute\s*\(\s*[\"'][^\"']*(\%s|\{|\$|format|f[\"'])[^\"']*[\"']"),
        "Potential SQL injection vulnerability"
    ),
    "hardcoded_secret": (
        re.compile(r"(api_key|api key|secret|password|token)\s*=\s*[\"'][a-zA-Z0-9_\-\.]{8,}[\"']", re.IGNORECASE),
        "Possible hardcoded secret or credential"
    ),
    "weak_crypto": (
        re.compile(r"\b(md5|sha1)\b", re.IGNORECASE),
        "Use of weak cryptographic hash function"
    ),
    "temp_file_risk": (
        re.compile(r"(tempfile\.mktemp|open\s*\(\s*[\"']/tmp/[^)]+\))",),
        "Insecure temporary file creation"
    ),
    "pickle_risk": (
        re.compile(r"\b(pickle\.load|pickle\.loads)\b"),
        "Pickle deserialization can lead to code execution"
    ),
    "yaml_risk": (
        re.compile(r"yaml\.load\s*\([^)]*Loader\s*=\s*None\)"),
        "Unsafe YAML loading (use yaml.safe_load instead)"
    ),
}


def lint_code(code: str) -> List[str]:
    """
    Check Python code for style issues according to Cherry's standards.
    
    This function analyzes code for style violations such as line length,
    variable naming practices, indentation, TODO comments, and more.
    It can optionally use external tools like flake8 if available.
    
    Args:
        code: The Python code string to check
        
    Returns:
        A list of warning messages for style issues found
        
    Example:
        >>> code = "def f(x):\\n  return x * 2  # TODO: improve this"
        >>> lint_code(code)
        ['Line 1: Function missing docstring', 'Line 1: Variable name too short (use descriptive names)', 
         'Line 2: Inconsistent indentation (use 4 spaces)', 'Line 2: TODO comment found']
    """
    warnings = []
    
    # Run pattern-based checks
    for pattern_name, (pattern, message) in STYLE_PATTERNS.items():
        for match in pattern.finditer(code):
            # Find the line number
            line_num = code[:match.start()].count('\n') + 1
            warnings.append(f"Line {line_num}: {message}")
    
    # Try to use flake8 if available (external tool check)
    try:
        # Create a temporary process to run flake8
        process = subprocess.run(
            ["flake8", "--stdin-display-name=code", "-"],
            input=code.encode(),
            capture_output=True,
            timeout=3  # Timeout after 3 seconds
        )
        
        if process.returncode == 0:
            # No flake8 issues found
            pass
        elif process.returncode == 1:
            # Found issues
            flake8_output = process.stdout.decode().strip()
            # Add flake8 findings to our warnings
            for line in flake8_output.split('\n'):
                if line.strip():
                    warnings.append(f"Flake8: {line}")
        else:
            # Error running flake8
            logger.warning(f"Flake8 exited with code {process.returncode}: {process.stderr.decode()}")
            
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        # Flake8 not available or failed, just continue with our own checks
        logger.debug(f"Couldn't run flake8: {e}")
    
    return warnings


def scan_security(code: str) -> List[str]:
    """
    Scan Python code for potential security vulnerabilities.
    
    This function analyzes code for common security concerns such as:
    - Use of dangerous functions like exec() or eval()
    - Potential command or SQL injection vulnerabilities
    - Hardcoded secrets or credentials
    - Use of weak cryptographic functions
    - Insecure file operations
    
    Args:
        code: The Python code string to scan
        
    Returns:
        A list of potential security issues found
        
    Example:
        >>> code = "def login():\\n    password = \\"hardcoded_secret\\"\\n    return eval(user_input)"
        >>> scan_security(code)
        ['Line 2: Possible hardcoded secret or credential', 'Line 3: Use of exec() or eval() is a security risk']
    """
    issues = []
    
    # Run pattern-based security checks
    for pattern_name, (pattern, message) in SECURITY_PATTERNS.items():
        for match in pattern.finditer(code):
            # Find the line number
            line_num = code[:match.start()].count('\n') + 1
            issues.append(f"Line {line_num}: {message}")
    
    # Additional heuristic checks that require more context
    
    # Check for unvalidated input usage in sensitive contexts
    input_vars = re.findall(r"(input\(\)|request\.form\[['\"][^'\"]+['\"]\]|request\.args\[['\"][^'\"]+['\"]\])", code)
    
    for input_var in input_vars:
        # Check if any of these inputs are used in dangerous contexts
        for i, line in enumerate(code.split('\n')):
            if input_var in line and any(keyword in line for keyword in ["exec", "eval", "subprocess", "os.system"]):
                issues.append(f"Line {i+1}: Unvalidated user input used in dangerous function")
    
    # Check for debug flags left on
    if re.search(r"DEBUG\s*=\s*True", code):
        issues.append("DEBUG flag is set to True")
    
    return issues


def check_code(code: str) -> Tuple[List[str], List[str]]:
    """
    Run both linting and security scans on code.
    
    Args:
        code: The Python code string to check
        
    Returns:
        A tuple containing (style_warnings, security_issues)
    """
    return lint_code(code), scan_security(code)


def _extract_line_from_code(code: str, line_num: int) -> str:
    """
    Extract a specific line from code for context.
    
    Args:
        code: The code string
        line_num: The line number to extract (1-based)
        
    Returns:
        The line content, or empty string if line doesn't exist
    """
    lines = code.split('\n')
    if 1 <= line_num <= len(lines):
        return lines[line_num - 1]
    return ""


def get_full_report(code: str) -> str:
    """
    Generate a comprehensive report of code quality and security.
    
    Args:
        code: The Python code string to check
        
    Returns:
        A formatted string with the full report
    """
    style_warnings, security_issues = check_code(code)
    
    report = []
    
    if style_warnings:
        report.append("Style Issues:")
        for warning in style_warnings:
            report.append(f"  • {warning}")
    else:
        report.append("No style issues found.")
    
    if security_issues:
        report.append("\nSecurity Issues:")
        for issue in security_issues:
            report.append(f"  • {issue}")
    else:
        report.append("\nNo security issues found.")
    
    # Add summary
    total_issues = len(style_warnings) + len(security_issues)
    if total_issues > 0:
        report.append(f"\nFound {total_issues} total issues ({len(style_warnings)} style, {len(security_issues)} security).")
    else:
        report.append("\nCode passed all checks!")
    
    return "\n".join(report)


# Sample usage
if __name__ == "__main__":
    # Sample code with various issues for demonstration
    sample_code = '''
import os, sys, subprocess

# TODO: Refactor this function
def authenticate(username, password="default_pwd"):
    """Check if user is valid"""
    # This is a very long comment that exceeds the recommended line length limit of 79 characters in PEP 8
    if username == "admin" and password == "secretpassword123":  # Hardcoded credential
        return True
    
    # Dangerous: allows command injection
    os.system("echo " + username)
    
    # Dangerous: allows code execution
    result = eval("username == 'admin'")
    
   # Inconsistent indentation
    query = "SELECT * FROM users WHERE username = '" + username + "'"  # SQL injection vulnerability
    
    api_key = "1a2b3c4d5e6f7g8h9i0j"  # Hardcoded API key
    
    # Using weak hash
    import hashlib
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    return False

'''
    
    print("Running code validation...\n")
    style_warnings, security_issues = check_code(sample_code)
    
    print("Style Issues:")
    for warning in style_warnings:
        print(f"  {warning}")
    
    print("\nSecurity Issues:")
    for issue in security_issues:
        print(f"  {issue}")
    
    print("\nFull Report:")
    print(get_full_report(sample_code))
