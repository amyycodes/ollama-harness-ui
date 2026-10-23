from dataclasses import dataclass

DEFAULT_MODEL = "llama3.2:3b"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_SYSTEM_PROMPT = (
    "You are a fast local coding agent. Read files before writing. "
    "Use tools sparingly. Keep responses concise and finish the task once evidence supports it."
)


@dataclass
class Settings:
    model: str = DEFAULT_MODEL
    ollama_base_url: str = OLLAMA_BASE_URL
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


SETTINGS = Settings()
