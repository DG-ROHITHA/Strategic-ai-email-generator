"""Configuration helpers for model and environment setup."""

import importlib
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

load_dotenv()


@dataclass
class AppConfig:
    """Config values loaded from .env and used by the UI."""

    openai_api_keys: list[str] = None
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.3
    base_url: str = ""
    ollama_model: str = "llama3.2:3b"
    ollama_base_url: str = "http://localhost:11434"

    def __post_init__(self):
        if self.openai_api_keys is None:
            self.openai_api_keys = []


def load_config() -> AppConfig:
    """Read configuration values from environment variables."""

    temperature_raw = os.getenv("OPENAI_TEMPERATURE", "0.3")
    try:
        parsed_temperature = float(temperature_raw)
    except ValueError:
        parsed_temperature = 0.3

    api_keys_raw = os.getenv("OPENAI_API_KEY", "")
    # Support comma-separated keys for rotation
    api_keys = [k.strip() for k in api_keys_raw.split(",") if k.strip()]

    return AppConfig(
        openai_api_keys=api_keys,
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=parsed_temperature,
        base_url=os.getenv("OPENAI_BASE_URL", ""),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def create_llm(
    api_key: str,
    model_name: str,
    temperature: float,
    base_url: str = "",
) -> BaseChatModel:
    """Create a LangChain ChatOpenAI model client."""

    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to call the model.")

    llm_kwargs = {
        "api_key": api_key,
        "model": model_name,
        "temperature": temperature,
    }

    if base_url.strip():
        llm_kwargs["base_url"] = base_url.strip()

    return ChatOpenAI(
        **llm_kwargs,
    )


def create_ollama_llm(
    model_name: str,
    temperature: float,
    base_url: str = "http://localhost:11434",
) -> BaseChatModel:
    """Create a LangChain ChatOllama client for local free inference."""

    try:
        module = importlib.import_module("langchain_ollama")
        chat_ollama_cls = getattr(module, "ChatOllama")
    except Exception as exc:
        raise ImportError(
            "langchain-ollama is required for Ollama mode. Install it with: pip install langchain-ollama"
        ) from exc

    return chat_ollama_cls(
        model=model_name,
        temperature=temperature,
        base_url=base_url.strip() or "http://localhost:11434",
    )
