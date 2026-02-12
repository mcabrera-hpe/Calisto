# Callisto - Implementation Plan

**Version:** Alpha  
**Timeline:** 2-3 weeks  
**Updated:** February 12, 2026

---

## Current Status (Updated: February 12, 2026)

### ✅ Completed
- **Phase 1 (Days 1-3): Foundation & Infrastructure** - 100% Complete
  - Docker environment fully configured and running (Weaviate 1.27.5)
  - **Migration from Ollama to External LLM API** - Complete
  - Project structure established with Poetry
  - Weaviate client upgraded to v4.19.0
  - Streamlit UI foundation built with tabs and navigation
  - Health check utilities implemented
  - Weaviate collections created (Document with multi-tenancy, ConversationHistory)
  - Tenants initialized (HPE, Toyota, Microsoft)
  - Basic scenario wizard UI created
  - Conversation display UI framework ready
  - **Proxy server for VPN environments** - Complete (proxy_server.py)

- **Phase 2 (Days 4-6): Agent Core & LLM Integration** - 100% Complete
  - Agent base class with external LLM API integration (src/agents/base.py)
  - MultiAgentOrchestrator with round-robin turn management (src/agents/orchestrator.py)
  - HumanAgent placeholder class
  - Conversation history tracking
  - Termination logic with keyword detection
  - Streaming conversation support (run_streaming)
  - Full integration with Streamlit UI
  - Real-time conversation display with agent metadata
  - Dynamic agent creation (2-5 agents) via hardcoded factory in api/helpers.py
  - Stop/restart conversation controls
  - **Code quality refactoring** - Score: 92.5/100 ✅
  
- **Phase 9 (Backend Split): FastAPI REST API** - 100% Complete
  - FastAPI backend with 4 REST endpoints (create, get, start, delete conversations)
  - In-memory conversation storage (POC-friendly, resets on restart)
  - Server-Sent Events (SSE) streaming for real-time conversation updates
  - Streamlit frontend refactored to call API instead of direct agent imports
  - Docker service separation (api:8000, app:8501)
  - CORS middleware for frontend/backend communication
  - Full end-to-end testing with curl validation

### ❌ Not Started
- **Phase 3 (Days 7-9):** LLM-Powered Scenario Generation - **Not implemented** (no mock, no LLM)
  - ❌ No suggest_agents_llm() function exists
  - ❌ No src/agents/factory.py module
  - ❌ No LLM-based agent generation
  - ✅ Basic hardcoded agent creation in api/helpers.py works
  
- **Phase 4 (Days 10-12):** RAG Pipeline - **Not started**
  - ❌ src/rag/ only contains __init__.py
  - ❌ No scripts/ingest_documents.py
  - ❌ llama-index-core dependency installed but unused

### 📋 Next Steps (Priority Order)
1. **LLM-powered agent suggestion** - Create suggest_agents_llm() function and factory.py module
2. **RAG Pipeline** - Document ingestion, LlamaIndex integration, multi-tenant retrieval
3. **Conversation persistence** - Save to Weaviate and JSON exports
4. **Sentiment analysis** - Real-time scoring with transformers
5. **Human-in-loop** - Connect HumanAgent to Streamlit chat_input

### 📊 Overall Progress: ~40% Complete (Revised)
- Infrastructure: 100% ✅
- Backend API: 100% ✅ (FastAPI REST API with SSE streaming)
- Core Agent System: 100% ✅ (basic hardcoded factory works)
- UI Framework: 100% ✅ (API-connected, functional for current features)
- **Agent Generation (LLM)**: 0% ❌ (hardcoded only, no LLM/mock)
- RAG Pipeline: 0% ❌
- Persistence: 0% ❌
- Documentation: 100% ✅
- Code Quality: 92.5/100 ✅

### 🎯 Next Milestone: Phase 3 - LLM Agent Suggestion
**Goal:** Create LLM-powered agent generation (no mock exists currently)  
**Timeline:** 1-2 days  
**Complexity:** Medium (~150 lines)
**Status:** Not started - currently using hardcoded agent factory in api/helpers.py

---

## Recent Major Changes (February 2026)

### 🔄 Migration from Ollama to External LLM API
**Date:** February 2026  
**Commits:** ffdacb6, aaa00a3

**Changes:**
- Removed Ollama container from docker-compose.yml
- Updated agents to call external LLM API endpoint (OpenAI-compatible)
- Environment variables: `LLM_API_ENDPOINT`, `LLM_API_TOKEN`, `DEFAULT_MODEL`
- Default model: `meta/llama-3.1-8b-instruct` (remote inference server)

**Impact:**
- Container count: 4 services → 3 services (app, api, weaviate)
- External dependency: Network access to LLM API required
- VPN compatibility: Requires proxy server (see below)

### 🌐 Proxy Server for VPN Environments
**Date:** February 2026  
**File:** [proxy_server.py](../proxy_server.py)

**Purpose:** Route Docker container requests to external LLM API through host VPN

**Architecture:**
```
Docker Container → host.docker.internal:7000 → Proxy (Flask) → VPN → External LLM API
```

**Configuration:**
- Proxy runs on host machine (port 7000)
- Containers use `LLM_API_ENDPOINT=http://host.docker.internal:7000/v1/chat/completions`
- Proxy forwards to production LLM API with SSL verification disabled
- See README for setup details

**Commands:**
- `make proxy-up` / `make proxy-down` - Start/stop proxy
- `make up` / `make down` - Start/stop proxy + containers

### 🏗️ Code Quality Refactoring
**Date:** February 5-6, 2026  
**Commits:** 56883cc, aaa00a3

**Changes:**
- Split [src/agents/core.py](../src/agents/core.py) into `base.py` + `orchestrator.py`
- Centralized config: [src/utils/config.py](../src/utils/config.py)
- Centralized logging: [src/utils/logging_config.py](../src/utils/logging_config.py)
- Added comprehensive type hints and docstrings
- Quality score: 68.6 → 92.5/100 (+23.9 points)

**Files Created:**
- `src/agents/base.py` - Agent and HumanAgent classes
- `src/agents/orchestrator.py` - MultiAgentOrchestrator
- `src/utils/config.py` - Shared environment variables
- `src/utils/logging_config.py` - Logging setup

---

## Phase Summary

### ✅ Phase 1-2: Foundation & Agent Core - Complete
Docker environment, external LLM API integration, agent classes, orchestrator, streaming UI

### ✅ Phase 9: FastAPI Backend - Complete  
REST API with SSE streaming, 4 endpoints, Streamlit → API integration

### ❌ Phase 3: LLM Agent Generation (Days 7-9) - Not Started
**Tasks:**
- Create `src/agents/suggester.py` with LLM prompt for agent generation
- Create `src/agents/factory.py` with agent creation logic
- Wire suggester → factory → orchestrator pipeline

### ❌ Phase 4: RAG Pipeline (Days 10-12) - Not Started  
**Tasks:**
- LlamaIndex integration
- Document ingestion script (`scripts/ingest_documents.py`)
- Multi-tenant document retrieval

### ❌ Phase 5-8: Additional Features - Not Started
- Persistence (Weaviate + JSON exports)
- Sentiment analysis (transformers)
- Human-in-loop mode
- Polish & documentation

---

## Alpha Release Checklist

### Infrastructure
- [x] Docker Compose with 3 services + proxy server configured
- [x] External LLM API integration working
- [x] Proxy server for VPN environments
- [x] Volume mounts for hot-reload

### Backend API
- [x] FastAPI with 4 REST endpoints
- [x] Pydantic validation
- [x] OpenAPI docs at /docs
- [x] SSE streaming
- [x] CORS configured

### Core Features
- [x] Agent LLM calls working (external API)
- [x] Multi-agent orchestrator complete
- [ ] LLM-powered agent generation ❌
- [ ] Dynamic agent factory ❌ (hardcoded only)
- [ ] Document ingestion CLI ❌
- [ ] Multi-tenant RAG ❌

### UI
- [x] Scenario wizard (client, description, num_agents)
- [x] Real-time conversation display (SSE streaming)
- [ ] Agent preview/regeneration ❌ (no LLM generation)
- [ ] Sentiment chart ❌ (placeholder)
- [ ] Past conversations tab ❌ (no persistence)
- [ ] Human input mode ❌ (not connected)

### Data & Persistence
- [x] Weaviate collections initialized
- [x] Multi-tenant setup (HPE, Toyota, Microsoft)
- [ ] Conversations saved to Weaviate ❌
- [ ] JSON exports ❌
- [ ] Sample data ingested ❌

### Testing
- [x] 2-5 agent conversations work via API
- [x] OpenAPI schema validates
- [ ] RAG retrieves tenant data ❌
- [ ] Sentiment analysis ❌
- [ ] Conversation replay ❌

---

## Commands

```bash
# Start everything
make up

# View logs
make logs-api    # Backend
make logs-app    # Frontend
make logs        # All services

# Stop
make down
make clean       # + remove volumes

# Rebuild
make build
make restart

# Proxy only
make proxy-up
make proxy-down

# Test
curl http://localhost:7000/health  # Proxy
curl http://localhost:8000/         # API
docker-compose exec app python scripts/init_weaviate.py
./run_tests.sh
```

---

## Project Structure

```
src/
├── api/            # ✅ FastAPI backend
│   ├── main.py         # Routes
│   ├── models.py       # Pydantic schemas
│   └── helpers.py      # Agent factory (hardcoded)
├── ui/             # ✅ Streamlit frontend
│   └── main.py         # UI app
├── agents/         # ✅ Agent classes
│   ├── base.py         # Agent + HumanAgent
│   ├── orchestrator.py # MultiAgentOrchestrator
│   └── core.py         # Re-exports
│   # ❌ factory.py - NOT CREATED
│   # ❌ suggester.py - NOT CREATED
├── rag/            # ❌ Not implemented
│   └── __init__.py
└── utils/          # ✅ Shared utilities
    ├── config.py       # Env vars
    └── logging_config.py

scripts/
├── init_weaviate.py        # ✅ Collection setup
├── test_agents.py          # ✅ Agent tests
├── test_api.py             # ✅ API tests
└── ingest_documents.py     # ❌ NOT CREATED

data/
├── conversations/          # Empty (no persistence)
└── documents/              # Sample data (not ingested)
```

---

## Future Enhancements

### Concurrent Multi-Scenario Execution
When deploying to cloud with concurrent users:
- Celery + Redis for async task queue
- SSE streaming for real-time tokens
- Worker orchestration
- ~8-10 days development

### Advanced Capabilities
- Scenario templates
- Agent role presets
- Multi-language support
- Enhanced sentiment analysis

### Analytics & Evaluation
- Phoenix observability
- MLflow experiment tracking
- RAGAS evaluation
- A/B testing framework

### Production Hardening
- Kubernetes deployment
- OAuth authentication
- Prometheus monitoring
- Performance optimization

---

## Timeline

```
Week 1: Foundation ✅ COMPLETE
├── Day 1-3: Infrastructure ✅
└── Day 4-6: Agent Core ✅

Week 2: Core Features ❌ NOT STARTED
├── Day 7-9: LLM Agent Generation ❌
└── Day 10-12: RAG Pipeline ❌

Week 3+: Remaining
├── Persistence ❌
├── Sentiment ❌
└── Human-in-loop ❌

Additional Work ✅ COMPLETE
├── External LLM Migration ✅
├── Proxy Server ✅
├── FastAPI Backend ✅
└── Code Quality (92.5/100) ✅

Current: 40% complete
Next: Phase 3 (LLM Agent Generation)
```
