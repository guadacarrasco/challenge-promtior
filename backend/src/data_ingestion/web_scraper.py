"""Web scraping module for Promtior website data ingestion"""

import logging
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

TARGET_URL = "https://www.promtior.ai"


def scrape_website(url: str = TARGET_URL) -> List[Document]:
    """
    Scrape content from the target website using LangChain's WebBaseLoader.

    Args:
        url: The URL to scrape

    Returns:
        List of Document objects with scraped content
    """
    try:
        logger.info(f"Starting web scrape of {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        logger.info(f"Successfully scraped {len(docs)} documents from {url}")
        for doc in docs:
            doc.metadata['source'] = url
            doc.metadata['type'] = 'website'
        
        return docs
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return []

