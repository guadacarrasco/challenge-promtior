import logging
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

TARGET_URL = "https://www.promtior.ai"


def scrape_website(url: str = TARGET_URL) -> List[Document]:
    
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        for doc in docs:
            doc.metadata['source'] = url
            doc.metadata['type'] = 'website'
        
        return docs
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return []

