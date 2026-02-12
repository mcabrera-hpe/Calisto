# VPN Proxy Setup

## Problem
Your Docker containers can't reach the external LLM API because your corporate VPN creates special routing rules on your Mac that containers don't inherit.

## Solution
Run a simple proxy server on your Mac that forwards requests from Docker containers to the external API.

## Steps

### 1. Install Flask (if needed)
```bash
pip3 install --user flask
# or
python3 -m pip install --user flask
```

### 2. Start the Proxy Server
In a **new terminal window**, run:
```bash
cd /Users/cabreram/DEV/Calisto
python3 proxy_server.py
```

You should see:
```
============================================================
LLM API Proxy Server
============================================================
Forwarding to: https://llama-3-1-8b-instruct-1...
Listening on: http://0.0.0.0:9000
Token configured: Yes

Docker containers should use:
  LLM_API_ENDPOINT=http://host.docker.internal:9000/v1/chat/completions
============================================================
```

**Keep this terminal window open** - the proxy needs to keep running.

### 3. Restart Docker Containers
In your **main terminal**:
```bash
docker-compose restart app api
```

### 4. Test the Connection
```bash
# Test that containers can reach the proxy  
docker-compose exec -T app python scripts/test_agents.py
```

You should now see agent messages being generated successfully!

## How It Works

```
Docker Container → http://host.docker.internal:9000 (proxy on Mac)
                ↓
Proxy forwards with VPN routing → https://10.182.9.173 (external API)
                ↓
Response ← Proxy ← External API
```

The proxy runs on your Mac where the VPN works, and Docker containers connect to it via `host.docker.internal` (Docker's special hostname for the host machine).

## Troubleshooting

**Proxy won't start?**
- Make sure port 9000 isn't already in use: `lsof -i :9000`
- Check Flask is installed: `python3 -c "import flask; print('Flask OK')"`

**Containers still can't connect?**
- Verify proxy is running: `curl http://localhost:9000/health`
- Should return: `{"status": "ok", "proxy": "LLM API Proxy"}`

**Proxy errors?**
- Check your VPN is connected
- Verify /etc/hosts has the DNS entry for the API
