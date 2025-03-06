import os
import json
from pathlib import Path

class CodeGenerator:
    """The builder agent - generates new components and boilerplate code"""
    
    def __init__(self):
        self.agent_id = "code_generator"
        self.specialties = ["component-creation", "boilerplate", "ui-implementation"]
        
    def generate_from_architecture(self):
        """Generate initial components from architecture.json"""
        # Load the architecture
        arch_path = Path(os.getcwd()) / "src" / "architecture.json"
        if not os.path.exists(arch_path):
            return {"success": False, "error": "Architecture definition not found"}
            
        with open(arch_path, "r") as f:
            architecture = json.load(f)
            
        # Generate tasks for AgentRunner to queue
        tasks = []
        
        # Create component tasks
        for component in architecture["components"]:
            tasks.append({
                "type": "generate-component",
                "data": {
                    "name": component["name"],
                    "type": component["type"],
                    "props": component["props"]
                }
            })
            
        # Create page container tasks
        for page in architecture["pages"]:
            tasks.append({
                "type": "write-file",
                "data": {
                    "filePath": f"src/containers/{page['name']}Page.jsx",
                    "content": self._generate_page_content(page, architecture["components"])
                }
            })
            
        # Create main App.jsx with router
        tasks.append({
            "type": "write-file",
            "data": {
                "filePath": "src/App.jsx",
                "content": self._generate_app_with_router(architecture["pages"])
            }
        })
        
        return {"success": True, "tasks": tasks}
        
    def _generate_page_content(self, page, components):
        """Generate a page container with its components"""
        # Build imports
        imports = [f"import {comp} from '../components/{comp}';" for comp in page["components"]]
        
        # Build JSX with props for each component
        components_jsx = []
        for comp_name in page["components"]:
            # Find the component definition
            comp_def = next((c for c in components if c["name"] == comp_name), None)
            if comp_def:
                # Generate props based on component definition
                props = []
                if "title" in comp_def.get("props", []):
                    props.append('title="{}"'.format(page["name"]))
                if "user" in comp_def.get("props", []):
                    props.append('user={{name: "User"}}')
                if "headline" in comp_def.get("props", []):
                    props.append('headline="Welcome to Cherry"')
                if "subtext" in comp_def.get("props", []):
                    props.append('subtext="Your AI-powered assistant"')
                if "ctaText" in comp_def.get("props", []):
                    props.append('ctaText="Get Started"')
                if "features" in comp_def.get("props", []):
                    props.append('features={[{title: "Feature 1", description: "Description"}, {title: "Feature 2", description: "Description"}]}')
                if "metrics" in comp_def.get("props", []):
                    props.append('metrics={{users: 100, tasks: 500}}')
                if "period" in comp_def.get("props", []):
                    props.append('period="weekly"')
                if "agents" in comp_def.get("props", []):
                    props.append('agents={["developer", "code_agent", "code_generator"]}')
                if "onActivate" in comp_def.get("props", []):
                    props.append('onActivate={() => console.log("Agent activated")}')
                    
                # Combine props
                props_str = " ".join(props)
                components_jsx.append(f"<{comp_name} {props_str} />")
            else:
                components_jsx.append(f"<{comp_name} />")
                
        components_jsx_str = "\n      ".join(components_jsx)
        
        return f"""import React from 'react';
{os.linesep.join(imports)}

const {page['name']}Page = () => {{
  return (
    <div className="cherry-page cherry-{page['name'].lower()}-page">
      {components_jsx_str}
    </div>
  );
}};

export default {page['name']}Page;
"""
        
    def _generate_app_with_router(self, pages):
        """Generate App.jsx with React Router setup"""
        imports = [f"import {page['name']}Page from './containers/{page['name']}Page';" for page in pages]
        
        routes = os.linesep.join([
            f'        <Route path="{page["route"]}" element={<{page["name"]}Page />} />'
            for page in pages
        ])
        
        return f"""import React from 'react';
import {{ BrowserRouter, Routes, Route }} from 'react-router-dom';
{os.linesep.join(imports)}

const App = () => {{
  return (
    <BrowserRouter>
      <Routes>
{routes}
      </Routes>
    </BrowserRouter>
  );
}};

export default App;
"""
