#!/usr/bin/env python3
"""
Cherry AI Codebase Analyzer
A tool to analyze and provide insights about the Cherry AI codebase.
"""

import os
import sys
import re
import json
from collections import defaultdict
import argparse
from typing import Dict, List, Tuple, Any


class CodebaseAnalyzer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.file_extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "markup": [".html", ".xml", ".md"],
            "config": [".json", ".yaml", ".yml", ".toml"],
            "style": [".css", ".scss", ".less"]
        }
        self.ignore_dirs = ["node_modules", ".git",
                            "__pycache__", "venv", "env", ".venv", "dist", "build"]
        self.stats = defaultdict(int)
        self.file_list = []
        self.api_endpoints = []
        self.imports = defaultdict(set)
        self.env_vars = set()

    def analyze(self):
        """Run all analysis methods"""
        self._collect_files()
        self._analyze_files()
        return {
            "stats": dict(self.stats),
            "api_endpoints": self.api_endpoints,
            "imports": {k: list(v) for k, v in self.imports.items()},
            "env_vars": list(self.env_vars)
        }

    def _collect_files(self):
        """Collect all relevant files in the codebase"""
        for root, dirs, files in os.walk(self.root_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)

                # Categorize file by extension
                for category, extensions in self.file_extensions.items():
                    if ext in extensions:
                        self.stats[f"{category}_files"] += 1
                        self.file_list.append((file_path, category))
                        break

    def _analyze_files(self):
        """Analyze collected files for various metrics"""
        for file_path, category in self.file_list:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Count lines of code
                    lines = content.split('\n')
                                                        self.stats["total_lines"] += len(lines)

                                    if __name__ == "__main__":
                                        parser = argparse.ArgumentParser(description="Analyze the Cherry AI codebase")
                                        parser.add_argument("--dir", default=".", help="Root directory to analyze")
                                        parser.add_argument("--output", help="Output file for JSON results")
                                        parser.add_argument("--report", help="Output file for human-readable report")
                                        args = parser.parse_args()

                                        analyzer = CodebaseAnalyzer(args.dir)
                                        results = analyzer.analyze()

                                        if args.output:
                                            with open(args.output, 'w') as f:
                                                json.dump(results, f, indent=2)
                                            print(f"JSON results written to {args.output}")
                                        else:
                                            print(json.dumps(results, indent=2))

                                        if args.report:
                                            report = analyzer.generate_report()
                                            with open(args.report, 'w') as f:
                                                f.write(report)
                                            print(f"Human-readable report written to {args.report}")
                                        else:
                                            print("\n" + analyzer.generate_report())

                                    # Analyze specific file types
                                    if category == "python":
                                        self._analyze_python_file(content, file_path)
                                    elif category in ["javascript", "typescript"]:
                                        self._analyze_javascript_file(content, file_path)
                            except Exception as e:
                                print(f"Error analyzing {file_path}: {e}", file=sys.stderr)

                    def _analyze_python_file(self, content: str, file_path: str):
                        """Analyze Python file for imports, API endpoints, etc."""
                        # Extract imports
                        import_pattern = re.compile(r'^import\s+(\w+)|^from\s+(\w+)')
                        for line in content.split('\n'):
                            match = import_pattern.match(line.strip())
                            if match:
                                module = match.group(1) or match.group(2)
                                self.imports[file_path].add(module)

                        # Look for Flask/FastAPI endpoints
                        endpoint_pattern = re.compile(r'@\w+\.route\([\'"]([^\'"]+)[\'"]')
                        for line in content.split('\n'):
                            match = endpoint_pattern.search(line)
                            if match:
                                self.api_endpoints.append(match.group(1))

                        # Look for environment variables
                        env_var_pattern = re.compile(r'os\.environ\.get\([\'"]([^\'"]+)[\'"]')
                        for line in content.split('\n'):
                            match = env_var_pattern.search(line)
                            if match:
                                self.env_vars.add(match.group(1))

                    def _analyze_javascript_file(self, content: str, file_path: str):
                        """Analyze JavaScript file for imports, API endpoints, etc."""
                        # Extract imports
                        import_pattern = re.compile(r'(import|require)\s*\(?[\'"]([^\'"]+)[\'"]')
                        for line in content.split('\n'):
                            match = import_pattern.search(line)
                            if match:
                                self.imports[file_path].add(match.group(2))

                        # Look for Express endpoints
                        endpoint_pattern = re.compile(r'(app|router)\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]')
                        for line in content.split('\n'):
                            match = endpoint_pattern.search(line)
                            if match:
                                self.api_endpoints.append(f"{match.group(2).upper()} {match.group(3)}")

                        # Look for environment variables
                        env_var_pattern = re.compile(r'process\.env\.([A-Z_]+)')
                        for line in content.split('\n'):
                            match = env_var_pattern.search(line)
                            if match:
                                self.env_vars.add(match.group(1))

                    def generate_report(self):
                        """Generate a human-readable report"""
                        report = []
                        report.append("# Cherry AI Codebase Analysis Report")
                        report.append("\n## Statistics")
                        report.append(f"- Total files analyzed: {sum(self.stats.get(f'{k}_files', 0) for k in self.file_extensions)}")
                        report.append(f"- Total lines of code: {self.stats.get('total_lines', 0)}")

                        for category in self.file_extensions:
                            report.append(f"- {category.capitalize()} files: {self.stats.get(f'{category}_files', 0)}")

                        report.append("\n## API Endpoints")
                        if self.api_endpoints:
                            for endpoint in sorted(self.api_endpoints):
                                report.append(f"- {endpoint}")
                        else:
                            report.append("- No API endpoints detected")

                        report.append("\n## Environment Variables")
                        if self.env_vars:
                            for var in sorted(self.env_vars):
                                report.append(f"- {var}")
                        else:
                            report.append("- No environment variables detected")

                        report.append("\n## Most Imported Modules")
                        module_counts = defaultdict(int)
                        for imports in self.imports.values():
                            for module in imports:
                                module_counts[module] += 1

                        for module, count in sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                            report.append(f"- {module}: {count} files")

                        return "\n".join(report)
