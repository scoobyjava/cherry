import os
import ast
import logging
import asyncio
from typing import Dict, Any, List, Tuple
import radon.complexity as cc
from cherry.agents.base_agent import Agent

logger = logging.getLogger(__name__)

class CodeAnalysisAgent(Agent):
    """
    Agent that analyzes code for issues, anti-patterns, and improvement opportunities.
    Provides feedback on code quality, maintainability, and performance.
    """
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.capabilities = [
            "code analysis", "code review", "performance analysis",
            "static analysis", "complexity analysis", "security audit",
            "refactoring suggestions", "documentation review"
        ]
        self._metrics_cache = {}
    
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a code analysis task.
        
        Args:
            task_data: Dictionary containing task details including:
                - code_path: Path to file or directory to analyze
                - focus_areas: Optional list of specific aspects to focus on
                
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Running code analysis on {task_data.get('code_path', 'provided code')}")
        
        # Extract relevant task information
        code_path = task_data.get('code_path')
        focus_areas = task_data.get('focus_areas', ['all'])
        code_content = task_data.get('code_content')
        
        if not code_path and not code_content:
            return {"error": "No code path or content provided for analysis"}
        
        results = {}
        analysis_tasks = []
        
        # Determine what to analyze based on focus areas
        if 'all' in focus_areas or 'complexity' in focus_areas:
            analysis_tasks.append(self._analyze_complexity(code_path, code_content))
            
        if 'all' in focus_areas or 'style' in focus_areas:
            analysis_tasks.append(self._analyze_style(code_path, code_content))
            
        if 'all' in focus_areas or 'security' in focus_areas:
            analysis_tasks.append(self._analyze_security(code_path, code_content))
            
        if 'all' in focus_areas or 'documentation' in focus_areas:
            analysis_tasks.append(self._analyze_documentation(code_path, code_content))
        
        # Run all analyses concurrently
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # Combine results
        for result in analysis_results:
            results.update(result)
        
        # Store analysis results in memory
        self.remember(f"analysis_{code_path}", results)
        
        # Generate summary of findings
        results["summary"] = self._generate_summary(results)
        results["improvement_suggestions"] = self._generate_improvement_suggestions(results)
        
        return results
    
    async def _analyze_complexity(self, code_path: str = None, code_content: str = None) -> Dict[str, Any]:
        """Analyze code complexity using metrics like cyclomatic complexity"""
        complexity_results = {"complexity": {"high_complexity_functions": []}}
        
        try:
            content = code_content if code_content else self._read_file(code_path)
            if not content:
                return {"complexity": {"error": "Could not read code content"}}
            
            # Use radon to analyze complexity
            complexity_metrics = cc.cc_visit(content)
            
            for metric in complexity_metrics:
                if metric.complexity > 10:  # High complexity threshold
                    complexity_results["complexity"]["high_complexity_functions"].append({
                        "name": metric.name,
                        "line": metric.lineno,
                        "complexity": metric.complexity
                    })
            
            # Add overall complexity rating
            avg_complexity = sum(m.complexity for m in complexity_metrics) / len(complexity_metrics) if complexity_metrics else 0
            complexity_results["complexity"]["average_complexity"] = avg_complexity
            complexity_results["complexity"]["rating"] = self._get_complexity_rating(avg_complexity)
            
        except Exception as e:
            logger.error(f"Error in complexity analysis: {str(e)}")
            complexity_results["complexity"]["error"] = str(e)
            
        return complexity_results
    
    async def _analyze_style(self, code_path: str = None, code_content: str = None) -> Dict[str, Any]:
        """Analyze code style and adherence to best practices"""
        style_results = {"style": {"issues":