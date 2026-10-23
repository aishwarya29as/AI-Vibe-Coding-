import os
from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "gemini-3.8-flash"


class SettingsError(ValueError):
    """Raised when application configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    model: str
    temperature: float


def load_settings() -> Settings:
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SettingsError(
            "GEMINI_API_KEY is missing. Create a .env file and set GEMINI_API_KEY."
        )

    raw_temperature = os.getenv("TEMPERATURE", "0.2")
    try:
        temperature = float(raw_temperature)
    except ValueError as exc:
        raise SettingsError(
            "TEMPERATURE must be a number between 0 and 2."
        ) from exc

    if not isfinite(temperature) or not 0 <= temperature <= 2:
        raise SettingsError("TEMPERATURE must be a number between 0 and 2.")

    return Settings(
        api_key=api_key,
        model=_get_model_name(),
        temperature=temperature,
    )


def get_model_name() -> str:
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
    return _get_model_name()


def _get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
