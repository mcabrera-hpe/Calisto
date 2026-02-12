#!/bin/bash
# Start the LLM API proxy server
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
poetry run python proxy_server.py
