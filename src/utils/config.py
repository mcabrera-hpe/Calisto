"""
Shared configuration for The Grid.

Centralized environment variable access to avoid duplication across modules.
"""

import os

# Service URLs
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

# External LLM API configuration
LLM_API_ENDPOINT = os.getenv(
    "LLM_API_ENDPOINT",
    "http://host.docker.internal:7000/v1/chat/completions"
)
LLM_API_TOKEN = os.getenv("LLM_API_TOKEN", "")

# Model configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Qwen/Qwen2.5-32B-Instruct")
