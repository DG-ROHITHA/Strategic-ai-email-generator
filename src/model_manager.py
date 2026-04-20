"""Model Manager: handles API key rotation and model fallback."""

import logging
from typing import Any, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from src.config import AppConfig, create_llm, create_ollama_llm

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages LLM instances with rotation and fallback capabilities."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.api_keys = config.openai_api_keys
        self.current_key_index = 0
        self._llm: Optional[BaseChatModel] = None

    def get_llm(self, force_fallback: bool = False) -> BaseChatModel:
        """Get the current LLM, or rotate/fallback if needed."""
        if force_fallback or not self.api_keys:
            logger.info("Using local fallback model (Ollama).")
            return create_ollama_llm(
                model_name=self.config.ollama_model,
                temperature=self.config.temperature,
                base_url=self.config.ollama_base_url
            )

        # Try to use current OpenAI key
        try:
            key = self.api_keys[self.current_key_index]
            return create_llm(
                api_key=key,
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                base_url=self.config.base_url
            )
        except Exception as e:
            logger.error(f"Error creating LLM with key {self.current_key_index}: {e}")
            return self.rotate_and_get_llm()

    def rotate_and_get_llm(self) -> BaseChatModel:
        """Rotate to the next API key and return a new LLM instance."""
        if not self.api_keys:
            return self.get_llm(force_fallback=True)

        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        # If we've circled back to the first key, fallback to local
        if self.current_key_index == 0:
            logger.warning("All OpenAI keys failed. Falling back to local model.")
            return self.get_llm(force_fallback=True)

        logger.info(f"Rotating to API key index {self.current_key_index}")
        return self.get_llm()

    def run_with_fallback(self, func, *args, **kwargs) -> Any:
        """Run a function with the LLM, automatically rotating on failure."""
        tries = len(self.api_keys) + 1 if self.api_keys else 1
        
        for _ in range(tries):
            try:
                llm = self.get_llm()
                return func(llm, *args, **kwargs)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                if "insufficient_quota" in str(e).lower() or "limit" in str(e).lower():
                    self.rotate_and_get_llm()
                else:
                    # For other errors, maybe try local fallback immediately or re-raise
                    return func(self.get_llm(force_fallback=True), *args, **kwargs)
        
        # Final attempt with local fallback if all else fails
        return func(self.get_llm(force_fallback=True), *args, **kwargs)
