#!/usr/bin/env python3
# filepath: /workspaces/cherry/src/agents/developer.py

import json
import argparse
import os
import sys
import re
from datetime import datetime
import hashlib

class DeveloperAgent:
    def __init__(self):
        self.agent_name = "developer"
        # Define sensitive patterns to avoid in generated code
        self.sensitive_patterns = [
            r'([\'"](?:api[_-]?key|api[_-]?secret|password|secret|token|key)[\'"]?\s*[:=]\s*[\'"])[^\'"]+([\'"])',
            r'([\'"](?:ACCESS[_-]?KEY|SECRET[_-]?KEY)[\'"]?\s*[:=]\s*[\'"])[^\'"]+([\'"])',
            r'([\'"](?:GITHUB[_-]?TOKEN)[\'"]?\s*[:=]\s*[\'"])[^\'"]+([\'"])'
        ]
    
    def design_website_structure(self, args=None):
        """
        Generate a comprehensive website architecture
        This defines the overall structure of the website, including
        components, pages, and their relationships
        """
        try:
            # Basic website architecture for demonstration
            architecture = {
                "components": {
                    "layout": [
                        {"name": "Header", "reusable": True, "children": ["Logo", "Navigation"]},
                        {"name": "Footer", "reusable": True, "children": ["SocialLinks", "Copyright"]},
                        {"name": "Sidebar", "reusable": True, "children": ["Categories", "RecentPosts"]}
                    ],
                    "ui": [
                        {"name": "Button", "variants": ["Primary", "Secondary", "Text"]},
                        {"name": "Card", "variants": ["Default", "Highlighted"]},
                        {"name": "Input", "variants": ["Text", "Select", "Checkbox"]}
                    ],
                    "content": [
                        {"name": "Hero", "children": ["Heading", "Subheading", "CallToAction"]},
                        {"name": "FeatureList", "children": ["Feature"]},
                        {"name": "Testimonials", "children": ["TestimonialCard"]}
                    ]
                },
                "pages": [
                    {
                        "name": "Home",
                        "path": "/",
                        "components": ["Header", "Hero", "FeatureList", "Testimonials", "Footer"]
                    },
                    {
                        "name": "About",
                        "path": "/about",
                        "components": ["Header", "Hero", "Content", "Team", "Footer"]
                    },
                    {
                        "name": "Contact",
                        "path": "/contact",
                        "components": ["Header", "ContactForm", "Map", "Footer"]
                    },
                    {
                        "name": "Projects",
                        "path": "/projects",
                        "components": ["Header", "ProjectGrid", "Pagination", "Footer"]
                    }
                ],
                "dataFlow": {
                    "sources": ["API", "LocalStorage", "Redux"],
                    "sinks": ["Components", "Analytics", "LocalStorage"]
                },
                "styling": {
                    "approach": "CSS-in-JS",
                    "tokens": {
                        "colors": {
                            "primary": "#3498db",
                            "secondary": "#2ecc71",
                            "text": "#333333",
                            "background": "#ffffff"
                        },
                        "typography": {
                            "fontFamily": "Inter, system-ui, sans-serif",
                            "sizes": {
                                "heading1": "2.5rem",
                                "heading2": "2rem",
                                "heading3": "1.5rem",
                                "body": "1rem"
                            }
                        },
                        "spacing": {
                            "small": "0.5rem",
                            "medium": "1rem",
                            "large": "2rem"
                        }
                    }
                }
            }
            
            # Add metadata and signatures
            result = {
                "success": True,
                "architecture": architecture,
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "agent": self.agent_name,
                    "checksum": self._generate_checksum(json.dumps(architecture))
                }
            }
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to design website structure: {str(e)}"
            }
    
    def review_code(self, args):
        """Review code for quality and security issues"""
        try:
            file_path = args.get("file_path")
            code = args.get("code")
            
            if not code and file_path:
                # Try to read code from file if provided
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        code = f.read()
                else:
                    return {
                        "success": False,
                        "error": f"File not found: {file_path}"
                    }
            
            if not code:
                return {
                    "success": False,
                    "error": "No code provided for review"
                }
            
            # Check for security issues
            security_issues = self._check_security(code)
            
            # Check for code quality issues
            quality_issues = self._check_code_quality(code)
            
            return {
                "success": True,
                "review": {
                    "security_issues": security_issues,
                    "quality_issues": quality_issues,
                    "summary": f"Found {len(security_issues)} security issues and {len(quality_issues)} quality issues",
                    "safe_to_deploy": len(security_issues) == 0
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Code review failed: {str(e)}"
            }
    

    def _check_security(self, code, file_path="unknown"):
        """Check code for security issues"""
        issues = []
        
        # Check for sensitive information
        for pattern in self.sensitive_patterns:
            for match in re.finditer(pattern, code):
                issues.append({
                    "filePath": file_path,
                    "type": "sensitive_data",
                    "description": "Potential sensitive data found",
                    "severity": "high",
                    # Redact the actual sensitive data in the report
                    "snippet": code[max(0, match.start() - 20):match.start()] + 
                              "[REDACTED]" +
                              code[match.end():min(len(code), match.end() + 20)]
                })
        
        # Check for other security patterns
        security_checks = [
            {
                "pattern": r"eval\s*\(",
                "description": "Potentially unsafe eval() usage",
                "severity": "high"
            },
            {
                "pattern": r"(?:exec|system|popen|subprocess\.call)\s*\(",
                "description": "Potential command injection",
                "severity": "high"
            },
            {
                "pattern": r"innerHTML|outerHTML",
                "description": "Potential XSS vulnerability",
                "severity": "medium"
            }
        ]
        
        for check in security_checks:
            for match in re.finditer(check["pattern"], code):
                issues.append({
                    "filePath": file_path,
                    "type": "security_issue",
                    "description": check["description"],
                    "severity": check["severity"],
                    "snippet": code[max(0, match.start() - 20):min(len(code), match.end() + 20)]
                })
        

        return issues    
    def _check_code_quality(self, code):
        """Check code for quality issues"""
        issues = []
        
        quality_checks = [
            {
                "pattern": r"console\.log",
                "description": "Debug statement found",
                "severity": "low"
            },
            {
                "pattern": r"TODO|FIXME",
                "description": "Incomplete code",
                "severity": "medium"
            },
            {
                "pattern": r"function\s+\w+\s*\([^)]{80,}\)",
                "description": "Function with too many parameters",
                "severity": "medium"
            }
        ]
        
        for check in quality_checks:
            for match in re.finditer(check["pattern"], code):
                issues.append({
                    "type": "quality_issue",
                    "description": check["description"],
                    "severity": check["severity"],
                    "snippet": code[max(0, match.start() - 20):min(len(code), match.end() + 20)]
                })
        
        return issues
    
    def create_api(self, args):
        """Create API endpoints for the website"""
        try:
            api_spec = args.get("api_spec", {})
            endpoints = []
            
            # Define default endpoints if none provided
            if not api_spec:
                endpoints = [
                    {
                        "path": "/api/projects",
                        "method": "GET",
                        "description": "Get all projects",
                        "params": [],
                        "response": {"type": "array", "items": {"type": "object"}}
                    },
                    {
                        "path": "/api/projects/{id}",
                        "method": "GET",
                        "description": "Get project by ID",
                        "params": [{"name": "id", "type": "string", "required": True}],
                        "response": {"type": "object"}
                    },
                    {
                        "path": "/api/contact",
                        "method": "POST",
                        "description": "Send contact message",
                        "params": [
                            {"name": "name", "type": "string", "required": True},
                            {"name": "email", "type": "string", "required": True},
                            {"name": "message", "type": "string", "required": True}
                        ],
                        "response": {"type": "object", "properties": {"success": {"type": "boolean"}}}
                    }
                ]
            else:
                endpoints = api_spec.get("endpoints", [])
            
            return {
                "success": True,
                "api": {
                    "endpoints": endpoints,
                    "documentation": self._generate_api_docs(endpoints)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"API creation failed: {str(e)}"
            }
    
    def _generate_api_docs(self, endpoints):
        """Generate API documentation"""
        docs = []
        for endpoint in endpoints:
            docs.append(f"## {endpoint.get('path')}\n\n"
                       f"**Method:** {endpoint.get('method')}\n\n"
                       f"**Description:** {endpoint.get('description')}\n\n"
                       f"**Parameters:**\n" +
                       "\n".join([f"- {p.get('name')} ({p.get('type')}): {'' if p.get('required') else 'Optional'}"
                                  for p in endpoint.get('params', [])]))
        
        return "\n\n".join(docs)
    
    def _generate_checksum(self, data):
        """Generate a checksum for data integrity"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

def main():
    parser = argparse.ArgumentParser(description='Developer Agent')
    parser.add_argument('--method', required=True, help='Method to call')
    parser.add_argument('--args', help='JSON file with arguments')
    parser.add_argument('--output', required=True, help='Output file path')
    
    args = parser.parse_args()
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    result = None
    method_args = {}
    if args.args:
        try:
            with open(args.args, 'r') as f:
                method_args = json.load(f)
        except Exception as e:
            result = {
                "success": False,
                "error": f"Failed to parse arguments file: {str(e)}"
            }
    
    if result is None:
        agent = DeveloperAgent()
        
        # Call the requested method if it exists
        if hasattr(agent, args.method) and callable(getattr(agent, args.method)):
            try:
                result = getattr(agent, args.method)(method_args)
            except Exception as e:
                result = {
                    "success": False,
                    "error": f"Method execution failed: {str(e)}",
                    "traceback": str(sys.exc_info())
                }
        else:
            result = {
                "success": False,
                "error": f"Unknown method: {args.method}"
            }
    
    # Write the result to the output file
    try:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"Error writing output file: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
