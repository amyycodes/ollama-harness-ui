import requests

from app.config import SETTINGS


class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or SETTINGS.ollama_base_url).rstrip("/")
        self.model = model or SETTINGS.model

    def chat(self, messages: list[dict[str, str]], stream: bool = False) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096,
            },
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()


def extract_message_content(resp: dict) -> str:
    if "message" in resp:
        return resp["message"].get("content", "")
    return resp.get("response", "")
