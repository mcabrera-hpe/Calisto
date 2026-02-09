# Callisto - Multi-Agent Conversation Simulator

Dockerized multi-agent conversation simulator for B2B PoC development. Agents use local Ollama LLMs to simulate business negotiations. Runs 100% locally.

---

## Quick Start

**Prerequisites:** Docker 20.10+, Docker Compose 2.0+, 16GB RAM

```bash
# Start services
docker-compose up -d

# Download LLM model (first time only)
docker-compose exec ollama ollama pull mistral

# Initialize Weaviate
docker-compose exec app python scripts/init_weaviate.py

# Access
open http://localhost:8501   # Streamlit UI
open http://localhost:8000/docs  # API docs (Swagger)
```

---

## Architecture

**4 containers:** `app` (Streamlit UI), `api` (FastAPI backend), `ollama` (LLM inference), `weaviate` (vector DB)

```
UI (Streamlit :8501) ──HTTP──▶ API (FastAPI :8000) ──imports──▶ Agents ──HTTP──▶ Ollama (:11434)
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

Set in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://ollama:11434` | LLM server |
| `WEAVIATE_URL` | `http://weaviate:8080` | Vector DB |
| `DEFAULT_MODEL` | `mistral` | LLM model |
| `MAX_TURNS` | `30` | Conversation turn limit |
| `API_URL` | `http://api:8000` | Backend URL (used by frontend) |

### Change LLM Model

```bash
docker-compose exec ollama ollama pull llama3.1
# Update DEFAULT_MODEL in docker-compose.yml, then:
make restart
```

---

## Monitoring Backend Activity

**Want to see what's happening behind the scenes?**

**Docker Desktop** (recommended): Open Docker Desktop → Containers → **callisto-api** → **Logs** tab, then start a conversation in the UI.

**CLI alternative:** `docker-compose logs -f api`

The Streamlit UI also shows detailed progress: "Turn 1/5 | Sarah responded in 87.3s | Next agent thinking..."

---

## Troubleshooting

```bash
docker-compose ps                    # Check service status
docker-compose logs -f api           # API logs
docker-compose logs -f ollama        # LLM logs
docker-compose exec ollama ollama list  # Verify models downloaded
```

**Out of memory?** Docker Desktop → Settings → Resources → Memory (set to 12GB+)

---

## Documentation

- [Implementation Plan](documentation/Implementation%20Plan%20-%20Callisto.md) — Roadmap and task backlog
- [Business Requirements](documentation/Business%20Requirements%20Document%20-%20Callisto.md) — Project charter and goals
