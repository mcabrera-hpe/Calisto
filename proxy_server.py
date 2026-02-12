#!/usr/bin/env python3
"""
Local proxy server to forward LLM API requests from Docker containers.

This proxy runs on the host machine (Mac) where VPN access works,
and forwards requests from Docker containers to the external LLM API.

Usage:
    python proxy_server.py

Then update docker-compose.yml to use:
    LLM_API_ENDPOINT=http://host.docker.internal:9000/v1/chat/completions
"""

from flask import Flask, request, Response
import requests
import os
import urllib3

# Suppress SSL warnings for internal network
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# External API configuration
API_URL = "https://llama-3-1-8b-instruct-1.umang-kedia-hpe-87bcba1f.serving.ai-application.shared08.vcfmr.local"
TOKEN = os.getenv("LLM_API_TOKEN", "")

if not TOKEN:
    # Try to read from .env file
    try:
        with open(".env") as f:
            for line in f:
                if line.startswith("LLM_API_TOKEN="):
                    TOKEN = line.split("=", 1)[1].strip()
                    break
    except FileNotFoundError:
        pass

if not TOKEN:
    print("WARNING: LLM_API_TOKEN not set. Requests will likely fail.")

@app.route('/v1/chat/completions', methods=['POST'])
def proxy_chat_completions():
    """Forward chat completion requests to external API."""
    try:
        print(f"Proxying request to {API_URL}/v1/chat/completions")
        
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
    print(f"Listening on: http://0.0.0.0:9001")
    print(f"Token configured: {'Yes' if TOKEN else 'No'}")
    print()
    print("Docker containers should use:")
    print("  LLM_API_ENDPOINT=http://host.docker.internal:9001/v1/chat/completions")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=9001, debug=False)
