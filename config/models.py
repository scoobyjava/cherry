from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: Optional[str] = Field(default="cherry_ai.log")


class MemoryConfig(BaseModel):
    provider: str = Field(default="chroma")
    persist_directory: str = Field(default="chroma_db")
    embedding_function: str = Field(default="openai")
    collection_name: str = Field(default="cherry_memory")


class LLMConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)
    api_key: Optional[str] = Field(default=None)


class AppConfig(BaseModel):
    app_name: str = Field(default="Cherry")
    debug: bool = Field(default=False)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)
