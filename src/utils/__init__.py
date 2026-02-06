"""
Utility modules for Callisto.

Provides shared configuration, logging, and helper functions.
"""

from .config import WEAVIATE_URL, OLLAMA_URL, DEFAULT_MODEL, MAX_TURNS
from .logging_config import setup_logging

__all__ = [
    'WEAVIATE_URL',
    'OLLAMA_URL', 
    'DEFAULT_MODEL',
    'MAX_TURNS',
    'setup_logging'
]
