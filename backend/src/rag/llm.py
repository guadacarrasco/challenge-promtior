

import logging
import os
from typing import Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    raise ImportError("Please install langchain-openai: pip install langchain-openai")

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAILLM:

    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
    ):
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not provided. Set it via environment variable or constructor."
            )
        
       
        
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )
        
        self.model_name = model
      
    
    def _build_messages(self, prompt: str, system_prompt: Optional[str] = None) -> list:
        """Build the message list, optionally prepending a system message."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        return messages

    def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
       
        try:
            messages = self._build_messages(prompt, system_prompt)
            response = self.llm.invoke(messages)
            text = response.content if hasattr(response, 'content') else str(response)

            return text
        except Exception as e:
            logger.error(f"Error invoking OpenAI: {str(e)}")
            raise
    
    def stream(self, prompt: str, system_prompt: Optional[str] = None):
        
        try:
            messages = self._build_messages(prompt, system_prompt)
            for chunk in self.llm.stream(messages):
                text = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if text:
                    yield text
        except Exception as e:
            logger.error(f"Error streaming from OpenAI: {str(e)}")
            raise
