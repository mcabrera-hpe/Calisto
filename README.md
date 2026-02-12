# Callisto - Multi-Agent Conversation Simulator

Dockerized multi-agent conversation simulator for B2B PoC development. Agents use external LLM API to simulate business negotiations.

**Goals:** Standardize agent infrastructure, reduce PoC time from days to hours, enable rapid model comparison  
**Status:** 40% complete — Core agent system working, RAG/persistence pending

---

## Quick Start

**Prerequisites:** Docker 20.10+, Docker Compose 2.0+, 8GB RAM, Python 3.11+, Poetry, Access to external LLM API

```bash
# Set your API token in .env file
# LLM_API_TOKEN="your-token-here"

# Start proxy server + all Docker services
make up

# Initialize Weaviate (first time only)
docker-compose exec app python scripts/init_weaviate.py

# Access
open http://localhost:8501   # Streamlit UI
open http://localhost:8000/docs  # API docs (Swagger)

# Stop everything
### VPN Proxy (if containers can't reach LLM API)

**Problem:** Corporate VPN routing doesn't work inside Docker containers  
**Solution:** Proxy server on host (port 7000) forwards requests through VPN

```bash
# Automatic (recommended)
make up                           # Starts proxy + containers

# Manual
./start-proxy.sh                  # In separate terminal
curl http://localhost:7000/health # Verify: {"status": "ok"}
docker-compose up -d              # Start containers
```

Containers use `LLM_API_ENDPOINT=http://host.docker.internal:7000/v1/chat/completions`

**Troubleshooting:**
- Port conflict? `lsof -i :7000` to check if port is in use
- Still failing? Verify VPN is connected, check DNS in /etc/hosts
```

**Note:** If you're on a corporate VPN, the proxy server automatically routes container requests to the external LLM API. See [VPN_PROXY_SETUP.md](VPN_PROXY_SETUP.md) for details.

---

## Architecture

**3 containers:** `app` (Streamlit UI), `api` (FastAPI backend), `weaviate` (vector DB)  
**External:** LLM API (remote inference server)

```
UI (Streamlit :8501) ──HTTP──▶ API (FastAPI :8000) ──imports──▶ Agents ──HTTPS──▶ External LLM API
```

### Project Structure

```
src/
├── api/            # FastAPI backend
│   ├── main.py         # Routes
│   ├── models.py       # Pydantic schemas
│   └── helpers.py      # Agent factory
├── ui/             # Streamlit frontend
│   └── main.py         # UI app
├── agents/         # Domain logic
│   ├── base.py         # Agent + HumanAgent classes
│   └── orchestrator.py # Conversation management
├── rag/            # RAG pipeline (planned)
└── utils/          # Shared config, logging
```

---

## API

FastAPI with auto-generated docs at **http://localhost:8000/docs**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/conversations` | Create conversation |
| `GET` | `/conversations/{id}` | Get conversation details |
| `POST` | `/conversations/{id}/start` | Start conversation (SSE stream) |
| `DELETE` | `/conversations/{id}` | Delete conversation |

**Example:**

```bash
# Create and run a conversation
curl -X POST http://localhost:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{"scenario":"Negotiate server purchase","client":"Toyota","num_agents":2,"max_turns":5}'
```

---

## Development

```bash
make up          # Start all services
make down        # Stop all services
make build       # Rebuild containers
make logs-api    # API logs
make logs-app    # Frontend logs
make clean       # Stop + remove volumes
```

Code changes in `src/` auto-reload via volume mounts.

### Configuration

Set in `docker-compose.yml` or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_ENDPOINT` | *[see .env]* | External LLM API URL |
| `LLM_API_TOKEN` | *[required]* | API authentication token |
| `WEAVIATE_URL` | `http://weaviate:8080` (container) / `http://localhost:8080` (host) | Vector DB |
| `DEFAULT_MODEL` | `meta/llama-3.1-8b-instruct` | LLM model identifier |
| `MAX_TURNS` | `30` | Conversation turn limit |

### Change LLM Model

Update `DEFAULT_MODEL` in `docker-compose.yml` to match a model available on your external LLM API, then:

```bash
make restart
```

---

## Monitoring Backend Activity

**Want to see what's happening behind the scenes?**

**Docker Desktop** (recommended): Open Docker Desktop → Containers → **callisto-api** → **Logs** tab, then start a conversation in the UI.

**CLI alternative:** `docker-compose logs -f api`

The Streamlit UI also shows detailed progress: "Turn 1/5 | Sarah responded in 87.3s | Next agent thinking..."

---

## Project Status

**Completed:**
- ✅ Docker infrastructure (3 services + proxy)
- ✅ FastAPI backend with SSE streaming
- ✅ Agent core (external LLM API integration)
- ✅ Streamlit UI for conversations
- ✅ Code quality: 92.5/100

**Next Steps:**
- LLM-powered agent generation (currently hardcoded)
- RAG pipeline with LlamaIndex
- Conversation persistence (Weaviate + JSON)
- Sentiment analysis integration

See [Implementation Plan](documentation/Implementation%20Plan%20-%20Callisto.md) for detailed roadmap
docker-compose logs -f api       # API logs
docker-compose logs -f app       # Frontend logs
```

**Network Issues?**  
If containers can't reach the external LLM API (common with corporate VPNs), use host networking mode (already configured in `docker-compose.yml`).

**API Token Expired?**  
Update `LLM_API_TOKEN` in `.env` file and restart: `docker-compose restart`

**Out of memory?**  
Docker Desktop → Settings → Resources → Memory (set to 8GB+)

---

## Documentation

- [Implementation Plan](documentation/Implementation%20Plan%20-%20Callisto.md) — Roadmap and task backlog
- [Business Requirements](documentation/Business%20Requirements%20Document%20-%20Callisto.md) — Project charter and goals
