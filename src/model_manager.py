"""Model Manager: handles Gemini model creation and fallback."""

import logging
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from src.config import AppConfig, create_gemini_llm

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages Gemini LLM instance."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._llm: Optional[BaseChatModel] = None

    def get_llm(self) -> BaseChatModel:
        """Get the Gemini LLM instance."""
        if self._llm is None:
            self._llm = create_gemini_llm(
                api_key=self.config.gemini_api_key,
                model_name=self.config.gemini_model,
                temperature=self.config.temperature,
            )
        return self._llm

    def run_with_fallback(self, func, *args, **kwargs) -> Any:
        """Run a function with the Gemini LLM."""
        try:
            llm = self.get_llm()
            return func(llm, *args, **kwargs)
        except Exception as e:
            logger.error(f"Gemini LLM call failed: {e}")
            raise
