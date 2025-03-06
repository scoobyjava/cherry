import os
import re
from pathlib import Path

class CodeAgent:
    """The craftsman agent - optimizes and refactors existing code"""
    
    def __init__(self):
        self.agent_id = "code_agent"
        self.specialties = ["optimization", "refactoring", "bug-fixing"]
        
    def optimize_component(self, component_path):
        """Optimize an existing component for performance"""
        if not os.path.exists(component_path):
            return {"success": False, "error": "Component not found"}
            
        with open(component_path, "r") as f:
            code = f.read()
            
        # Apply optimizations based on detected patterns
        optimized_code = self._apply_performance_optimizations(code)
        
        # Write optimized code back
        with open(component_path, "w") as f:
            f.write(optimized_code)
            
        return {"success": True, "path": component_path}
        
    def _apply_performance_optimizations(self, code):
        """Apply various optimization techniques"""
        # Add memo for expensive calculations
        if "useEffect" in code and re.search(r'const\s+\w+\s*=\s*calculate', code):
            code = re.sub(
                r'(const\s+)(\w+)(\s*=\s*calculate[^;]+;)', 
                r'const \2 = useMemo(() => calculate\3, []);', 
                code
            )
        
        # Prevent unnecessary re-renders with React.memo
        if "export default" in code and not "React.memo" in code:
            code = re.sub(
                r'export default (\w+);', 
                r'export default React.memo(\1);', 
                code
            )
                
        return code
