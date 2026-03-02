"""LLM initialization with Ollama and LLaMA2"""

import logging
import os
from typing import Optional

try:
    from langchain_community.llms import Ollama
except ImportError:
    raise ImportError("Please install langchain and langchain-community")

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_BASE_URL = "http://ollama:11434"
DEFAULT_MODEL = "llama3.2:1b"


class OllamaLLM:
    """Wrapper for Ollama LLM"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
    ):
        """
        Initialize Ollama LLM.
        
        Args:
            base_url: Base URL for Ollama server
            model: Model name (default: llama2)
            temperature: Temperature for generation (0-1)
        """
        base_url = base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
        
        logger.info(f"Initializing Ollama LLM at {base_url} with model {model}")
        
        # Only use parameters supported by llama2
        # Removed: mirostat, mirostat_tau, mirostat_eta, tfs_z (cause warnings)
        self.llm = Ollama(
            base_url=base_url,
            model=model,
            temperature=temperature,
            top_p=0.9,
            top_k=40,
        )
        
        self.model_name = model
        logger.info(f"Ollama LLM initialized successfully")
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        try:
            logger.debug(f"Invoking Ollama with prompt: {prompt[:100]}...")
            response = self.llm.invoke(prompt)
            logger.debug(f"Got response: {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"Error invoking Ollama: {str(e)}")
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
            logger.debug(f"Streaming from Ollama with prompt: {prompt[:100]}...")
            for chunk in self.llm.stream(prompt):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.error(f"Error streaming from Ollama: {str(e)}")
            raise
