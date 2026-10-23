import logging

from google import genai
from google.genai.errors import APIError
from google.genai import types

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    """Raised when a Gemini request fails without exposing SDK details."""


class GeminiService:
    def __init__(self, settings: Settings, client: genai.Client | None = None) -> None:
        self._settings = settings
        self._client = (
            client
            if client is not None
            else genai.Client(api_key=settings.api_key)
        )

    def generate_answer(self, history: list[dict[str, str]]) -> str:
        contents = [
            types.Content(
                role="model" if message["role"] == "assistant" else "user",
                parts=[types.Part.from_text(text=message["content"])],
            )
            for message in history
        ]
        try:
            response = self._client.models.generate_content(
                model=self._settings.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=self._settings.temperature,
                ),
            )
        except APIError as exc:
            logger.error("Gemini API request failed (%s).", type(exc).__name__)
            raise GeminiServiceError(
                "The Gemini request failed. Please try again."
            ) from None

        answer = response.text
        if not answer:
            logger.error("Gemini API returned an empty response.")
            raise GeminiServiceError(
                "Gemini returned an empty response. Please try again."
            )
        logger.info("Gemini response generated (model=%s).", self._settings.model)
        return answer
