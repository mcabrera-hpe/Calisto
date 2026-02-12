"""
Utility modules for Callisto.

Provides shared configuration, logging, and helper functions.
"""

from .config import WEAVIATE_URL, LLM_API_ENDPOINT, LLM_API_TOKEN, DEFAULT_MODEL, MAX_TURNS
from .logging_config import setup_logging

__all__ = [
    'WEAVIATE_URL',
    'LLM_API_ENDPOINT',
    'LLM_API_TOKEN',
    'DEFAULT_MODEL',
    'MAX_TURNS',
    'setup_logging'
]
