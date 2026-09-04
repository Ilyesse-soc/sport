from abc import ABC, abstractmethod
import base64
import httpx
import json

from app.core.config import get_settings


class AIProvider(ABC):
    @abstractmethod
    async def text(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def vision_estimate(self, image_bytes: bytes, mime_type: str, prompt: str) -> dict:
        raise NotImplementedError


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def text(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.gemini_api_key:
            return "Je n'ai pas de cle Gemini configuree. Je te donne une reponse basee sur les donnees disponibles uniquement."
        url = (
            f"{self.base_url}/{self.settings.gemini_model}:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.3},
        }
        data = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    break
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
                if attempt == 2:
                    return "Service IA temporairement indisponible. Reessaie dans quelques instants."
        if not data:
            return "Service IA temporairement indisponible."
        return (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "Je n'ai pas pu generer de reponse.")
        )

    async def vision_estimate(self, image_bytes: bytes, mime_type: str, prompt: str) -> dict:
        if not self.settings.gemini_api_key:
            return {
                "confidence": "faible",
                "disclaimer": "Estimation approximative sans vision IA activee.",
                "items": [],
            }
        url = (
            f"{self.base_url}/{self.settings.gemini_model}:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(image_bytes).decode("utf-8"),
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.2},
        }
        data = None
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=35.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    break
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
                if attempt == 1:
                    return {
                        "confidence": "faible",
                        "disclaimer": "Estimation indisponible pour le moment.",
                        "items": [],
                    }
        if not data:
            return {
                "confidence": "faible",
                "disclaimer": "Estimation indisponible pour le moment.",
                "items": [],
            }
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "{}")
        )
        raw = text[:5000]
        try:
            parsed = json.loads(raw)
            items = parsed.get("items", []) if isinstance(parsed, dict) else [{"raw_response": raw}]
        except Exception:
            items = [{"raw_response": raw}]
        return {
            "confidence": "moyenne",
            "disclaimer": "Estimation IA non exacte, a confirmer.",
            "items": items,
        }


def get_ai_provider() -> AIProvider:
    return GeminiProvider()
