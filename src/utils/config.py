"""
Shared configuration for Callisto.

Centralized environment variable access to avoid duplication across modules.
"""

import os

# Service URLs
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

# Model configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
MAX_TURNS = int(os.getenv("MAX_TURNS", "30"))
