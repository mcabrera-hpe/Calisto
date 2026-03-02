#!/usr/bin/env python3
"""
Local proxy server to forward LLM API requests from Docker containers.

This proxy runs on the host machine (Mac) where VPN access works,
and forwards requests from Docker containers to the external LLM API.

Usage:
    python proxy_server.py

Then update docker-compose.yml to use:
    LLM_API_ENDPOINT=http://host.docker.internal:7000/v1/chat/completions
"""

from flask import Flask, request, Response
import requests
import os
import urllib3

# Suppress SSL warnings for internal network
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

def _read_env_file(key: str) -> str:
    """Read a value from .env file as fallback."""
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
    except FileNotFoundError:
        pass
    return ""

# External API configuration - all values from environment
API_URL = os.getenv("LLM_API_BASE_URL") or _read_env_file("LLM_API_BASE_URL")
TOKEN = os.getenv("LLM_API_TOKEN") or _read_env_file("LLM_API_TOKEN")

if not API_URL:
    print("WARNING: LLM_API_BASE_URL not set. Proxy cannot forward requests.")
if not TOKEN:
    print("WARNING: LLM_API_TOKEN not set. Requests will likely fail.")

@app.route('/v1/chat/completions', methods=['POST'])
def proxy_chat_completions():
    """Forward chat completion requests to external API."""
    print(f"[PROXY] Received POST to /v1/chat/completions from {request.remote_addr}")
    print(f"[PROXY] Content-Type: {request.content_type}")
    print(f"[PROXY] Headers: {dict(request.headers)}")
    try:
        print(f"[PROXY] Forwarding to {API_URL}/v1/chat/completions")
        
        resp = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            },
            json=request.json,
            verify=False,  # Skip SSL verification for internal network
            timeout=120
        )
        
        print(f"Response status: {resp.status_code}")
        
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
        
    except Exception as e:
        print(f"Proxy error: {e}")
        return {"error": str(e)}, 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return {"status": "ok", "proxy": "LLM API Proxy"}

if __name__ == '__main__':
    print("=" * 60)
    print("LLM API Proxy Server")
    print("=" * 60)
    print(f"Forwarding to: {API_URL}")
    print(f"Listening on: http://0.0.0.0:7000")
    print(f"Token configured: {'Yes' if TOKEN else 'No'}")
    print()
    print("Docker containers should use:")
    print("  LLM_API_ENDPOINT=http://host.docker.internal:7000/v1/chat/completions")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=7000, debug=False)
