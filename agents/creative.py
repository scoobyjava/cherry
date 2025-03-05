import json
from typing import Dict, List, Any, Optional
from agents.base import BaseAgent
from logger import get_logger

logger = get_logger(__name__)

class CreativeAgent(BaseAgent):
    """Agent for generating creative content like writing, ideas, and designs."""
    
    def __init__(self, config: Dict[str, Any], memory=None):
        super().__init__(config, memory)
        self.creative_styles = {
            "concise": "Clear, direct and to-the-point",
            "detailed": "Rich with details and elaboration",
            "innovative": "Novel, unique and unconventional",
            "practical": "Realistic, implementable and pragmatic",
            "artistic": "Aesthetic, expressive and emotionally rich"
        }
        self.default_style = "detailed"
        
    async def generate_creative_content(self, prompt: str, content_type: str = "writing", 
                                        style: str = None, additional_context: Dict = None) -> Dict:
        """
        Generate creative content based on a prompt.
        
        Args:
            prompt: The user's creative request
            content_type: Type of content (writing, idea, design)
            style: Creative style to apply
            additional_context: Additional context or constraints
            
        Returns:
            Dict containing the generated content
        """
        style = style or self.default_style
        style_guidance = self.creative_styles.get(style, self.creative_styles[self.default_style])
        
        context = {}
        if additional_context:
            context.update(additional_context)
            
        if self.memory:
            # Retrieve relevant creative context if available
            relevant_context = await self.memory.search(prompt, limit=3)
            if relevant_context:
                context["inspirations"] = relevant_context
        
        system_prompt = self._get_system_prompt(content_type, style_guidance)
        user_prompt = self._format_user_prompt(prompt, content_type, context)
        
        response = await self.llm(
            system=system_prompt,
            user=user_prompt
        )
        
        # Save the generated content to memory if available
        if self.memory:
            await self.memory.add(
                {
                    "prompt": prompt,
                    "content_type": content_type,
                    "style": style,
                    "response": response
                }
            )
            
        result = {
            "content": response,
            "content_type": content_type,
            "style": style
        }
        
        return result
    
    async def generate_writing(self, prompt: str, style: str = None, 
                               format: str = "essay", length: str = "medium") -> Dict:
        """Generate creative writing content."""
        context = {
            "format": format,
            "length": length
        }
        return await self.generate_creative_content(prompt, "writing", style, context)
    
    async def generate_ideas(self, prompt: str, style: str = None, 
                             count: int = 5, domain: str = None) -> Dict:
        """Generate creative ideas based on a prompt."""
        context = {
            "count": count,
            "domain": domain
        }
        return await self.generate_creative_content(prompt, "ideas", style, context)
    
    async def generate_design(self, prompt: str, style: str = None, 
                              medium: str = None, constraints: List[str] = None) -> Dict:
        """Generate creative design concepts."""
        context = {
            "medium": medium,
            "constraints": constraints or []
        }
        return await self.generate_creative_content(prompt, "design", style, context)
    
    async def refine_content(self, content: str, feedback: str) -> Dict:
        """Refine previously generated content based on feedback."""
        system_prompt = """You are a skilled creative content refiner. Your task is to improve 
        the provided content based on specific feedback while maintaining the original intent and style."""
        
        user_prompt = f"""Please refine the following content based on the feedback provided:
        
        ORIGINAL CONTENT:
        {content}
        
        FEEDBACK:
        {feedback}
        
        Provide an improved version that addresses the feedback while maintaining the essence of the original."""
        
        response = await self.llm(
            system=system_prompt,
            user=user_prompt
        )
        
        return {
            "refined_content": response,
            "original_content": content,
            "feedback": feedback
        }
    
    def _get_system_prompt(self, content_type: str, style_guidance: str) -> str:
        """Get appropriate system prompt based on content type and style."""
        base_prompt = f"""You are an expert creative content generator specialized in {content_type}. 
        Your style should be {style_guidance}."""
        
        if content_type == "writing":
            return base_prompt + """ Create engaging, original written content that captures the essence 
            of the given prompt. Balance creativity with clarity and structure."""
            
        elif content_type == "ideas":
            return base_prompt + """ Generate innovative, useful ideas that address the prompt. 
            Each idea should be distinct and provide a fresh perspective."""
            
        elif content_type == "design":
            return base_prompt + """ Conceptualize design solutions that are both aesthetic and functional. 
            Consider user experience, visual appeal, and practical implementation."""
            
        return base_prompt
    
    def _format_user_prompt(self, prompt: str, content_type: str, context: Dict) -> str:
        """Format the user prompt with appropriate instructions based on content type."""
        user_prompt = f"PROMPT: {prompt}\n\n"
        
        if content_type == "writing":
            format_type = context.get("format", "essay")
            length = context.get("length", "medium")
            user_prompt += f"""Please create a {length} {format_type} based on this prompt. 
            Make it engaging and well-structured."""
            
        elif content_type == "ideas":
            count = context.get("count", 5)
            domain = context.get("domain")
            domain_text = f" in the {domain} domain" if domain else ""
            user_prompt += f"""Generate {count} creative ideas{domain_text} based on this prompt. 
            Format each idea with a title and brief description."""
            
        elif content_type == "design":
            medium = context.get("medium")
            constraints = context.get("constraints", [])
            user_prompt += f"""Create a design concept{f' for {medium}' if medium else ''} based on this prompt."""
            if constraints:
                user_prompt += "\nPlease work within these constraints:\n"
                for constraint in constraints:
                    user_prompt += f"- {constraint}\n"
        
        if "inspirations" in context:
            user_prompt += "\nYou may draw inspiration from these related items:\n"
            for insp in context["inspirations"]:
                user_prompt += f"- {insp}\n"
                
        return user_prompt
