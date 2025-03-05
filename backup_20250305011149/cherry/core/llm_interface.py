from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass
