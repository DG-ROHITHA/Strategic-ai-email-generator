"""Configuration helpers for model and environment setup."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


@dataclass
class AppConfig:
    """Config values loaded from .env and used by the UI."""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    temperature: float = 0.3

    @property
    def openai_api_key(self):
        """Legacy compat — returns empty string."""
        return ""

    @property
    def openai_api_keys(self):
        """Legacy compat — returns list with gemini key if available."""
        return [self.gemini_api_key] if self.gemini_api_key else []


def load_config() -> AppConfig:
    """Read configuration values from environment variables."""

    temperature_raw = os.getenv("GEMINI_TEMPERATURE", os.getenv("OPENAI_TEMPERATURE", "0.3"))
    try:
        parsed_temperature = float(temperature_raw)
    except ValueError:
        parsed_temperature = 0.3

    return AppConfig(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=parsed_temperature,
    )


def create_gemini_llm(
    api_key: str,
    model_name: str = "gemini-2.0-flash",
    temperature: float = 0.3,
) -> BaseChatModel:
    """Create a LangChain ChatGoogleGenerativeAI model client."""

    if not api_key:
        raise ValueError("GEMINI_API_KEY is required to call the model.")

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=temperature,
    )


# Legacy aliases so existing imports don't break immediately
def create_llm(api_key: str = "", model_name: str = "", temperature: float = 0.3, base_url: str = "") -> BaseChatModel:
    """Legacy wrapper — redirects to Gemini."""
    config = load_config()
    return create_gemini_llm(
        api_key=config.gemini_api_key or api_key,
        model_name=config.gemini_model,
        temperature=temperature,
    )


def create_ollama_llm(model_name: str = "", temperature: float = 0.3, base_url: str = "") -> BaseChatModel:
    """Legacy wrapper — redirects to Gemini (Ollama no longer used)."""
    config = load_config()
    return create_gemini_llm(
        api_key=config.gemini_api_key,
        model_name=config.gemini_model,
        temperature=temperature,
    )
