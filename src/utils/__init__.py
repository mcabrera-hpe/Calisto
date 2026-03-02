"""
Utility modules for The Grid.

Provides shared configuration, logging, and helper functions.
"""

from .config import WEAVIATE_URL, LLM_API_ENDPOINT, LLM_API_TOKEN, DEFAULT_MODEL
from .logging_config import setup_logging

__all__ = [
    'WEAVIATE_URL',
    'LLM_API_ENDPOINT',
    'LLM_API_TOKEN',
    'DEFAULT_MODEL',
    'setup_logging'
]
