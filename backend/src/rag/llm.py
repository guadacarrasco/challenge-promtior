"""LLM initialization with OpenAI"""

import logging
import os
from typing import Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
except ImportError:
    raise ImportError("Please install langchain-openai: pip install langchain-openai")

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"


class OllamaLLM:
    """Wrapper for OpenAI LLM (maintains same interface as Ollama)"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
    ):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini - fast and cost-effective)
            temperature: Temperature for generation (0-1)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not provided. Set it via environment variable or constructor."
            )
        
        logger.info(f"Initializing OpenAI LLM with model {model}")
        
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )
        
        self.model_name = model
        logger.info(f"OpenAI LLM initialized successfully")
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        try:
            logger.debug(f"Invoking OpenAI with prompt: {prompt[:100]}...")
            response = self.llm.invoke([HumanMessage(content=prompt)])
            text = response.content if hasattr(response, 'content') else str(response)
            logger.debug(f"Got response: {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Error invoking OpenAI: {str(e)}")
            raise
    
    def stream(self, prompt: str):
        """
        Stream responses from the LLM token by token.
        
        Args:
            prompt: Input prompt
            
        Yields:
            Text chunks from the LLM
        """
        try:
            logger.debug(f"Streaming from OpenAI with prompt: {prompt[:100]}...")
            for chunk in self.llm.stream([HumanMessage(content=prompt)]):
                text = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if text:
                    yield text
        except Exception as e:
            logger.error(f"Error streaming from OpenAI: {str(e)}")
            raise
