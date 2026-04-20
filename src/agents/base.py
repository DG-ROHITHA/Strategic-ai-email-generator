"""Shared base class used by all agents."""

from typing import Any, Dict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from src.utils import parse_json_response


class BaseAgent:
    """Simple wrapper around a prompt template plus LLM invocation."""

    def __init__(self, llm: BaseChatModel, prompt_template: str, agent_name: str) -> None:
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        self.agent_name = agent_name

    def invoke(self, **kwargs: Any) -> str:
        """Invoke the model with formatted messages and return raw text."""

        messages = self.prompt.format_messages(**kwargs)
        response = self.llm.invoke(messages)
        content = getattr(response, "content", "")
        return content if isinstance(content, str) else str(content)

    def invoke_json(self, default: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Invoke model and safely parse a JSON dictionary response."""

        raw_response = self.invoke(**kwargs)
        return parse_json_response(raw_response, default)
