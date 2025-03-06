import json
import os
from pathlib import Path

class Developer:
    """The architect agent - handles system design and code organization"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.agent_id = "developer"
        self.specialties = ["architecture", "system-design", "code-structure"]
        
    def design_website_structure(self):
        """Create initial website structure and architecture"""
        # Define key pages and components
        website_structure = {
            "pages": [
                {"name": "Home", "route": "/", "components": ["Header", "HeroSection", "FeatureGrid", "Footer"]},
                {"name": "Dashboard", "route": "/dashboard", "components": ["Header", "DashboardStats", "AgentStatus", "Footer"]}
            ],
            "components": [
                {"name": "Header", "type": "functional", "props": ["title", "user"]},
                {"name": "Footer", "type": "functional", "props": []},
                {"name": "HeroSection", "type": "functional", "props": ["headline", "subtext", "ctaText"]},
                {"name": "FeatureGrid", "type": "functional", "props": ["features"]},
                {"name": "DashboardStats", "type": "class", "props": ["metrics", "period"]},
                {"name": "AgentStatus", "type": "class", "props": ["agents", "onActivate"]}
            ],
            "dataFlow": {
                "auth": "Context API",
                "metrics": "API Fetch + Local Storage",
                "agentStatus": "WebSocket"
            }
        }
        
        # Save the structure for other agents to use
        output_dir = Path(os.getcwd()) / "src"
        os.makedirs(output_dir, exist_ok=True)
        output_path = output_dir / "architecture.json"
        
        with open(output_path, "w") as f:
            json.dump(website_structure, f, indent=2)
            
        return website_structure
