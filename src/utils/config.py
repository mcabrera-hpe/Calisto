"""
Shared configuration for Callisto.

Centralized environment variable access to avoid duplication across modules.
"""

import os

# Service URLs
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

# External LLM API configuration
LLM_API_ENDPOINT = os.getenv(
    "LLM_API_ENDPOINT",
    "https://llama-3-1-8b-instruct-1.umang-kedia-hpe-87bcba1f.serving.ai-application.shared08.vcfmr.local/v1/chat/completions"
)
LLM_API_TOKEN = os.getenv("LLM_API_TOKEN", "")

# Model configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "meta/llama-3.1-8b-instruct")
MAX_TURNS = int(os.getenv("MAX_TURNS", "30"))
