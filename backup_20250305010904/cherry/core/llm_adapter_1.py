from .llm_interface.py import LLMInterface

class LLMAdapter1(LLMInterface):
    def generate_text(self, prompt: str) -> str:
        # Implementation for LLM 1
        return "Generated text from LLM 1"
