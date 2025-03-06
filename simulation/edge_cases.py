import random
import asyncio
from typing import Dict, Any

class EdgeCaseGenerator:
    """Generates challenging edge cases for Cherry to handle"""
    
    @staticmethod
    async def malformed_input_test() -> Dict[str, Any]:
        """Generate test with malformed inputs"""
        malformed_cases = [
            {"type": "code_fix", "language": "python", 
             "code": "def function(x, y,,,): return x++y"},
            
            {"type": "code_fix", "language": None,  # None where string expected
             "code": "function test() { return []; },"},
            
            {"type": "feature_design", "domain": "web", 
             "requirements": [None, 123, {"invalid": "structure"}]},
             
            {"type": "deployment", "component": "",  # Empty string
             "target": ""}
        ]
        return random.choice(malformed_cases)
    
    @staticmethod
    async def timeout_simulation() -> Dict[str, Any]:
        """Generate test that simulates network timeouts"""
        await asyncio.sleep(random.uniform(1.5, 3.0))  # Long delay
        raise TimeoutError("Network connection timed out")
    
    @staticmethod
    async def concurrent_operation_test(count: int = 5) -> Dict[str, Any]:
        """Test handling multiple operations at once"""
        # Create multiple concurrent tasks
        async def single_op(idx):
            await asyncio.sleep(random.uniform(0.1, 0.5))
            if random.random() < 0.3:  # 30% chance of failure
                raise Exception(f"Concurrent operation {idx} failed")
            return {"status": "success", "operation_id": idx}
            
        tasks = [single_op(i) for i in range(count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "type": "concurrent_test",
            "operations": count,
            "results": results,
            "success_rate": len([r for r in results if not isinstance(r, Exception)]) / count
        }