from dataclasses import dataclass

DEFAULT_MODEL = "llama3.2:3b"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_SYSTEM_PROMPT = (
    "You are an SWE (software engineering) agent working locally in a codebase. "
    "Your job is to complete the user request fully and correctly before stopping. "
    "Read the relevant files before making changes. Prefer minimal, targeted actions. "
    "Do not finish early or claim success before the task is actually done. "
    "If more evidence is needed, continue gathering it; if the request is complete, stop. "
    "Keep outputs concise, actionable, and grounded in the codebase."
)


@dataclass
class Settings:
    model: str = DEFAULT_MODEL
    ollama_base_url: str = OLLAMA_BASE_URL
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


SETTINGS = Settings()
