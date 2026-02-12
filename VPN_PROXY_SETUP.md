# VPN Proxy Setup

## Problem
Your Docker containers can't reach the external LLM API because your corporate VPN creates special routing rules on your Mac that containers don't inherit.

## Solution
Run a simple proxy server on your Mac that forwards requests from Docker containers to the external API.

## Steps

### 1. Start the Proxy Server (Easy Way)
Use the Makefile to start everything:
```bash
cd /Users/cabreram/DEV/Calisto
make up
```

This automatically starts the proxy server and Docker containers.

### 2. Start the Proxy Server (Manual Way)
In a **new terminal window**, run:
```bash
cd /Users/cabreram/DEV/Calisto
./start-proxy.sh
```

You should see:
```
============================================================
LLM API Proxy Server
============================================================
Forwarding to: https://llama-3-1-8b-instruct-1...
Listening on: http://0.0.0.0:7000
Token configured: Yes

Docker containers should use:
  LLM_API_ENDPOINT=http://host.docker.internal:7000/v1/chat/completions
============================================================
```

**Keep this terminal window open** - the proxy needs to keep running.

### 3. Verify the Proxy is Running
In your **main terminal**:
```bash
curl http://localhost:7000/health
```

You should see: `{"status": "ok", "proxy": "LLM API Proxy"}`

### 4. Restart Docker Containers (if already running)
If your Docker containers are already running:
```bash
docker-compose restart app api
```

Otherwise, start everything using:
```bash
make up
```

### 5. Test the Connection
```bash
# Test that containers can reach the proxy  
docker-compose exec -T app python scripts/test_agents.py
```

You should now see agent messages being generated successfully!

## How It Works

```
Docker Container → http://host.docker.internal:7000 (proxy on Mac)
                ↓
Proxy forwards with VPN routing → https://external-api (external API)
                ↓
Response ← Proxy ← External API
```

The proxy runs on your Mac where the VPN works, and Docker containers connect to it via `host.docker.internal` (Docker's special hostname for the host machine).

## Troubleshooting

**Proxy won't start?**
- Make sure port 7000 isn't already in use: `lsof -i :7000`
- Check Flask is installed: `poetry run python -c "import flask; print('Flask OK')"`

**Containers still can't connect?**
- Verify proxy is running: `curl http://localhost:7000/health`
- Should return: `{"status": "ok", "proxy": "LLM API Proxy"}`

**Proxy errors?**
- Check your VPN is connected
- Verify /etc/hosts has the DNS entry for the API
