#!/usr/bin/env python3
"""
Code Analyzer - Identifies overly complex implementations across the codebase.
Analyzes function and method lengths to highlight potential refactoring targets.
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Set


@dataclass
class FunctionInfo:
    """Store information about functions and methods."""
    name: str
    start_line: int
    end_line: int
    line_count: int
    file_path: str
    language: str
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "line_count": self.line_count,
            "file_path": self.file_path,
            "language": self.language,
        }


class CodeAnalyzer:
    def __init__(self, 
                 root_dir: str, 
                 exclude_dirs: List[str] = None,
                 complexity_thresholds: Dict[str, int] = None):
        """
        Initialize the code analyzer.
        
        Args:
            root_dir: Root directory to start the analysis
            exclude_dirs: Directories to exclude from analysis
            complexity_thresholds: Dictionary mapping file extensions to line count thresholds
        """
        self.root_dir = Path(root_dir)
        self.exclude_dirs = set(exclude_dirs or ['node_modules', 'venv', '.git', '__pycache__'])
        
        # Default thresholds for different languages
        self.complexity_thresholds = complexity_thresholds or {
            '.py': 50,    # Python
            '.js': 40,    # JavaScript
            '.jsx': 40,   # React JSX
            '.ts': 40,    # TypeScript
            '.tsx': 40,   # React TypeScript
            '.java': 50,  # Java
            '.go': 50,    # Go
            '.rb': 40,    # Ruby
            '.php': 50,   # PHP
            '.cs': 50,    # C#
            '.cpp': 50,   # C++
            '.c': 50,     # C
            '.rs': 50,    # Rust
        }
        
        self.language_patterns = {
            '.py': {
                'function': r'def\s+([a-zA-Z0-9_]+)\s*\(.*\):',
                'class_method': r'def\s+([a-zA-Z0-9_]+)\s*\(self,.*?\):',
                'static_method': r'def\s+([a-zA-Z0-9_]+)\s*\(cls,.*?\):',
                'block_end': r'^\s*$|^\s*def\s+|^\s*class\s+'
            },
            '.js': {
                'function': r'function\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*{',
                'arrow_function': r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:\(.*\)|[a-zA-Z0-9_]+)\s*=>\s*{',
                'method': r'(?:async\s+)?([a-zA-Z0-9_]+)\s*\(.*\)\s*{',
                'block_end': r'^\s*}$'
            },
            '.ts': {
                'function': r'function\s+([a-zA-Z0-9_]+)\s*\(.*\)(?:\s*:\s*\w+)?\s*{',
                'arrow_function': r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:\(.*\)|[a-zA-Z0-9_]+)\s*=>\s*{',
                'method': r'(?:async\s+)?([a-zA-Z0-9_]+)\s*\(.*\)(?:\s*:\s*\w+)?\s*{',
                'block_end': r'^\s*}$'
            }
        }
        
        # Apply the same patterns to similar languages
        self.language_patterns['.jsx'] = self.language_patterns['.js']
        self.language_patterns['.tsx'] = self.language_patterns['.ts']

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from analysis."""
        for part in path.parts:
            if part in self.exclude_dirs:
                return True
        return False

    def get_file_extension(self, file_path: Path) -> str:
        """Get the file extension in lowercase."""
        return file_path.suffix.lower()

    def analyze_file(self, file_path: Path) -> List[FunctionInfo]:
        """Analyze a single file to find functions and their lengths."""
        file_ext = self.get_file_extension(file_path)
        
        # Skip if we don't have patterns for this language
        if file_ext not in self.language_patterns:
            return []
        
        functions: List[FunctionInfo] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            patterns = self.language_patterns[file_ext]
            
            # Process each line to find functions and their boundaries
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check for function declarations
                func_name = None
                for pattern_type, pattern in patterns.items():
                    if pattern_type != 'block_end':
                        match = re.search(pattern, line)
                        if match:
                            func_name = match.group(1)
                            start_line = i + 1
                            
                            # Find the end of the function
                            j = i + 1
                            brace_count = 1 if '{' in line else 0
                            
                            # Different ending detection for different languages
                            if file_ext == '.py':
                                # For Python, track indentation
                                func_indent = len(line) - len(line.lstrip())
                                while j < len(lines):
                                    next_line = lines[j]
                                    if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= func_indent:
                                        if not re.match(r'^\s*@', next_line):  # Skip decorators
                                            break
                                    j += 1
                            else:
                                # For languages with braces
                                while j < len(lines) and brace_count > 0:
                                    next_line = lines[j]
                                    brace_count += next_line.count('{') - next_line.count('}')
                                    j += 1
                            
                            end_line = j
                            line_count = end_line - start_line
                            
                            functions.append(FunctionInfo(
                                name=func_name,
                                start_line=start_line,
                                end_line=end_line,
                                line_count=line_count,
                                file_path=str(file_path),
                                language=file_ext[1:]  # Remove the leading dot
                            ))
                            break
                
                i += 1
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            
        return functions

    def analyze_codebase(self) -> List[FunctionInfo]:
        """Analyze the entire codebase to find complex functions."""
        all_functions: List[FunctionInfo] = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Modify dirs in-place to exclude directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            path = Path(root)
            if self.should_exclude(path):
                continue
                
            for file in files:
                file_path = path / file
                file_ext = self.get_file_extension(file_path)
                
                # Skip if we don't have a threshold for this extension
                if file_ext not in self.complexity_thresholds:
                    continue
                    
                functions = self.analyze_file(file_path)
                all_functions.extend(functions)
                
        return all_functions
    
    def filter_complex_functions(self, functions: List[FunctionInfo]) -> List[FunctionInfo]:
        """Filter functions that exceed the complexity threshold."""
        complex_functions = []
        
        for func in functions:
            file_ext = f".{func.language}"
            if file_ext in self.complexity_thresholds:
                threshold = self.complexity_thresholds[file_ext]
                if func.line_count > threshold:
                    complex_functions.append(func)
                    
        return complex_functions
    
    def generate_report(self, complex_functions: List[FunctionInfo], output_file: Optional[str] = None):
        """Generate a report of complex functions."""
        # Sort by line count (descending)
        complex_functions.sort(key=lambda x: x.line_count, reverse=True)
        
        report = {
            "summary": {
                "total_complex_functions": len(complex_functions),
                "language_breakdown": {}
            },
            "functions": [func.to_dict() for func in complex_functions]
        }
        
        # Generate language breakdown
        for func in complex_functions:
            lang = func.language
            if lang not in report["summary"]["language_breakdown"]:
                report["summary"]["language_breakdown"][lang] = 0
            report["summary"]["language_breakdown"][lang] += 1
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Analyze code complexity across a codebase')
    parser.add_argument('--root', type=str, default='.', help='Root directory to analyze')
    parser.add_argument('--output', type=str, help='Output JSON file for the report')
    parser.add_argument('--exclude', type=str, nargs='+', default=['node_modules', 'venv', '.git', '__pycache__'],
                        help='Directories to exclude from analysis')
    parser.add_argument('--thresholds', type=str, help='JSON file with custom thresholds')
    
    args = parser.parse_args()
    
    complexity_thresholds = None
    if args.thresholds:
        with open(args.thresholds, 'r') as f:
            complexity_thresholds = json.load(f)
    
    analyzer = CodeAnalyzer(args.root, args.exclude, complexity_thresholds)
    all_functions = analyzer.analyze_codebase()
    complex_functions = analyzer.filter_complex_functions(all_functions)
    
    report = analyzer.generate_report(complex_functions, args.output)
    
    # Print a summary to the console
    print(f"Found {len(complex_functions)} complex functions out of {len(all_functions)} total functions.")
    print("Top 10 most complex functions:")
    for i, func in enumerate(complex_functions[:10], 1):
        print(f"{i}. {func.name} ({func.line_count} lines) in {func.file_path}:{func.start_line}")
    
    if not args.output:
        print("\nRun with --output to save the full report to a JSON file.")


if __name__ == "__main__":
    main()
