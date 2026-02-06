# Callisto - Implementation Plan

**Project:** Multi-Agent Conversation Simulator  
**Version:** Alpha  
**Date:** January 30, 2026 (Updated: February 2, 2026)  
**Timeline:** 2-3 weeks

---

## Current Status (Updated: February 5, 2026)

### ✅ Completed
- **Phase 1 (Days 1-3): Foundation & Infrastructure** - 100% Complete
  - Docker environment fully configured and running (Weaviate 1.27.5, Ollama with llama3.1)
  - Project structure established with Poetry
  - Weaviate client upgraded to v4.19.0
  - Streamlit UI foundation built with tabs and navigation
  - Health check utilities implemented
  - Weaviate collections created (Document with multi-tenancy, ConversationHistory)
  - Tenants initialized (HPE, Toyota, Microsoft)
  - Basic scenario wizard UI created
  - Conversation display UI framework ready

- **Phase 2 (Days 4-6): Agent Core & LLM Integration** - 100% Complete
  - Agent base class with Ollama HTTP integration (src/agents/core.py)
  - MultiAgentOrchestrator with round-robin turn management
  - HumanAgent placeholder class
  - Conversation history tracking
  - Termination logic with keyword detection
  - Streaming conversation support (run_streaming)
  - Full integration with Streamlit UI
  - Real-time conversation display with agent metadata
  - Dynamic agent creation (2-5 agents)
  - Stop/restart conversation controls
  
### 🚧 In Progress
- **Phase 3 (Days 7-9):** LLM-Powered Scenario Generation - Mock only
- **Phase 4 (Days 10-12):** RAG Pipeline - Not started

### 📋 Next Steps (Priority Order)
1. **FastAPI Backend Split** - Minimal API wrapper for cloud deployment readiness (~1 day)
2. **LLM-powered agent suggestion** - Replace mock suggest_agents_llm() with real LLM call
3. **RAG Pipeline** - Document ingestion, LlamaIndex integration, multi-tenant retrieval
4. **Conversation persistence** - Save to Weaviate and JSON exports
5. **Sentiment analysis** - Real-time scoring with transformers
6. **Human-in-loop** - Connect HumanAgent to Streamlit chat_input

### 📊 Overall Progress: ~40% Complete
- Infrastructure: 100% ✅
- Core Agent System: 90% ✅ (missing: LLM agent generation)
- UI Framework: 70% ✅ (missing: sentiment chart, human input)
- Backend API: 0% (Phase 9 planned)
- RAG Pipeline: 0%
- Persistence: 0%
- Documentation: 100% ✅

### 🎯 Next Milestone: Phase 9 - FastAPI Backend Split
**Goal:** Cloud-ready API architecture  
**Timeline:** 1 day  
**Complexity:** Minimal (~100 new lines, POC-compliant)

---

## Overview

This document outlines the phased implementation plan for building Callisto, a local multi-agent conversation simulator for rapid PoC development.

**Implementation Strategy:** Build incrementally, test frequently, keep it simple.

---

## Phase 1: Foundation & Infrastructure (Days 1-3)

### Goals
- Get basic Docker environment running
- Establish project structure
- Verify all services communicate

### Tasks

#### Day 1: Project Setup
- [x] Create project directory structure
- [x] Initialize Poetry project with `pyproject.toml`
- [x] Create `docker-compose.yml` with 3 services (app, weaviate, ollama)
- [x] Create basic `Dockerfile` for app container
- [x] Create `.dockerignore` and `.gitignore`
- [x] Test: `docker-compose up` successfully starts all containers

#### Day 2: Service Configuration
- [x] Configure Weaviate with multi-tenancy enabled
- [x] Pull Ollama models (llama3.1, nomic-embed-text)
- [x] Create health check scripts for each service
- [x] Create `scripts/init_weaviate.py` to initialize collections
- [x] Test: All health checks pass, Weaviate schema created

#### Day 3: Basic Connectivity
- [x] Create simple Streamlit app in `src/app.py` (Hello World)
- [x] Test HTTP connection to Ollama from app container
- [x] Test HTTP connection to Weaviate from app container
- [x] Create `.streamlit/config.toml` for UI customization
- [x] Test: Streamlit accessible at localhost:8501, can ping Ollama and Weaviate

**Deliverables:**
- Working Docker Compose environment
- All services healthy and communicating
- Basic Streamlit UI rendering

**Acceptance:**
- Run `docker-compose up`, access http://localhost:8501
- No errors in logs
- Can manually call Ollama API: `curl http://localhost:11434/api/generate`

---

## Phase 2: Agent Core & LLM Integration (Days 4-6) ✅ COMPLETED

### Goals
- Build agent classes and orchestration
- Implement direct Ollama calls
- Get agents talking to each other autonomously
- **Skip RAG for now** - agents can talk without external data

### Tasks

#### Day 4: Agent Base Class
- [x] Create `src/agents/core.py` with simple Agent class
- [x] Implement `Agent.respond()` with direct Ollama HTTP calls
- [x] Test: Single agent responds to a message
- [x] Add basic system prompt support

#### Day 5: Orchestrator & Multi-Turn
- [x] Implement `MultiAgentOrchestrator` class in `core.py`
- [x] Add round-robin turn management
- [x] Implement conversation history tracking
- [x] Test: 2 agents have a 5-turn conversation (command line test)

#### Day 6: UI Integration
- [x] Connect orchestrator to Streamlit UI
- [x] Replace mock agent generation with real agent creation
- [x] Implement auto-run conversation when user clicks "Start Conversation"
- [x] Add streaming display with run_streaming()
- [x] Test: End-to-end UI flow with real agent conversation
- [x] Added: Dynamic 2-5 agent support
- [x] Added: Stop/restart controls
- [x] Added: Generation time display per message

**Deliverables:**
- ✅ Working Agent class with LLM integration
- ✅ Basic orchestration for multi-turn conversations
- ✅ Agents conversing in the UI

**Acceptance:**
- ✅ Create 2-5 agents via UI, click "Start Conversation"
- ✅ Agents respond coherently using Ollama
- ✅ Conversation completes without errors
- ✅ Messages display in UI in real-time with streaming

---

## Phase 3: LLM-Powered Scenario Generation (Days 7-9)

### Goals
- Build agent classes and orchestration
- Implement direct Ollama calls
- Create basic conversation flow

### Tasks

#### Day 7: Agent Classes
- [ ] Create `src/agents/core.py` with Agent base class
- [ ] Implement direct Ollama HTTP calls in Agent.respond()
- [ ] Add streaming support for real-time token display
- [ ] Create HumanAgent class (waits for user input)
- [ ] Test: Agent can respond to simple message

#### Day 8: Orchestrator
- [ ] Implement MultiAgentOrchestrator class
- [ ] Add round-robin turn management
- [ ] Implement conversation history tracking
- [ ] Add termination logic (max turns, sentiment thresholds)
- [ ] Test: 2 agents can have 5-turn conversation

#### Day 9: Tool Integration
- [ ] Connect RAGTool to agents
- [ ] Implement tool assignment based on role keywords
- [ ] Add agent system prompt generation
- [ ] Test: Agent uses RAG to answer question about company data

**Deliverables:**
- Working agent system with LLM integration
- Basic orchestration for multi-turn conversations
- Agents can use RAG tools

**Acceptance:**
- Manually create 2 agents, run conversation
- Agents respond coherently using Ollama
- RAG tool provides relevant context
- Conversation completes without errors

---

## Phase 4: RAG Pipeline with LlamaIndex (Days 10-12)

### Goals
- Build scenario wizard UI
- Implement LLM-based agent suggestion
- Dynamic agent configuration

### Tasks

#### Day 10: Few-Shot Prompt Engineering
- [ ] Create `src/agents/suggester.py` with scenario prompt template
- [ ] Write 3-4 diverse few-shot examples
- [ ] Test prompt with different scenarios (sales, multi-party, etc.)
- [ ] Refine prompt for consistent JSON output
- [ ] Test: LLM generates valid agent configurations

#### Day 11: Agent Factory
- [ ] Create `src/agents/factory.py` with generate_agent() function
- [ ] Implement LLM-based system prompt generation
- [ ] Add tool assignment logic (keyword + LLM fallback)
- [ ] Test: Factory creates complete agent from JSON config

#### Day 12: Integration & Testing
- [ ] Wire suggester → factory → orchestrator pipeline
- [ ] Test end-to-end: describe scenario → get agents → run conversation
- [ ] Handle edge cases (invalid JSON, missing fields)
- [ ] Add retry logic for failed LLM calls

**Deliverables:**
- LLM-powered scenario wizard
- Dynamic agent generation pipeline
- End-to-end automation (description → running agents)

**Acceptance:**
- Input: "HPE selling servers to Toyota"
- Output: 2 appropriate agents with roles, prompts, tools
- Agents execute conversation successfully

---

## Phase 5: Streamlit UI Development (Days 13-15)

### Goals
- Build interactive scenario wizard
- Create conversation display
- Add sentiment visualization

### Tasks

#### Day 13: Scenario Wizard Interface
- [ ] Create sidebar form (client dropdown, scenario textarea, participate checkbox)
- [ ] Implement "Generate Agents" button
- [ ] Display generated agent preview
- [ ] Add "Run Simulation" and "Regenerate" buttons
- [ ] Test: User flow from input to agent preview

#### Day 14: Conversation Display
- [ ] Create chat-style message display
- [ ] Show agent name (Company - Role) for each message
- [ ] Implement streaming message updates
- [ ] Add turn counter and metrics sidebar
- [ ] Test: Conversation renders clearly in real-time

#### Day 15: Sentiment & Visualization
- [ ] Install transformers for sentiment analysis
- [ ] Implement per-turn sentiment scoring
- [ ] Create real-time sentiment chart (Streamlit line_chart)
- [ ] Add final metrics display (total turns, outcome)
- [ ] Test: Sentiment updates live during conversation

**Deliverables:**
- Complete Streamlit UI
- Real-time conversation display
- Sentiment visualization

**Acceptance:**
- User can create scenario via wizard
- Conversation displays with streaming responses
- Sentiment chart shows progression
- UI is intuitive and responsive

---

## Phase 6: Persistence & Replay (Days 16-17)

### Goals
- Save conversations to Weaviate
- Export JSON backups
- Load and replay past conversations

### Tasks

#### Day 16: Conversation Storage
- [ ] Create `src/utils/persistence.py` with save_conversation()
- [ ] Implement Weaviate ConversationHistory insertion
- [ ] Implement JSON export to `data/conversations/`
- [ ] Store full agent configs including generated prompts
- [ ] Test: Conversation saved successfully after completion

#### Day 17: Replay & History
- [ ] Create "Past Conversations" tab in Streamlit
- [ ] Query Weaviate for conversation list
- [ ] Implement filtering by client and date
- [ ] Display conversation replay with all messages
- [ ] Show metrics summary (turns, sentiment, outcome)
- [ ] Test: Load conversation from last week, displays correctly

**Deliverables:**
- Full persistence layer
- JSON exports for backup
- Conversation replay functionality

**Acceptance:**
- Run conversation, find it in "Past Conversations" tab
- Replay shows exact same messages and metrics
- JSON file exists in `data/conversations/`

---

## Phase 7: Human-in-the-Loop Mode (Days 18-19)

### Goals
- Enable user participation in conversations
- Seamless switching between autonomous and interactive modes
- Handle human turn in orchestrator

### Tasks

#### Day 18: Human Agent Implementation
- [ ] Implement HumanAgent.respond() to await Streamlit input
- [ ] Update orchestrator to detect HumanAgent
- [ ] Add Streamlit chat_input for user messages
- [ ] Implement session state management for interactive conversations
- [ ] Test: User can respond as company agent

#### Day 19: UI Refinement
- [ ] Add "Start Conversation" button for interactive mode
- [ ] Clear visual indicator when waiting for user input
- [ ] Display user messages differently from AI messages
- [ ] Add "End Conversation" button
- [ ] Test: Complete human-AI conversation works smoothly

**Deliverables:**
- Working human-in-the-loop mode
- Clear UI for human participation
- Session state properly managed

**Acceptance:**
- Check "I want to participate" box
- System generates client agent + human agent
- User can chat with AI client agent
- Conversation saves with human messages marked

---

## Phase 8: Polish & Documentation (Days 20-21)

### Goals
- Create comprehensive documentation
- Add sample data
- Final testing and bug fixes

### Tasks

#### Day 20: Documentation
- [ ] Write README.md with setup instructions
- [ ] Create quick start guide
- [ ] Document ingestion script usage
- [ ] Add troubleshooting section
- [ ] Create architecture diagram
- [ ] Test: Fresh user can set up from README

#### Day 21: Final Testing & Samples
- [ ] Create sample documents for all 3 companies
- [ ] Test all user flows end-to-end
- [ ] Fix any bugs found during testing
- [ ] Optimize slow operations
- [ ] Create demo scenarios YAML (for future reference)
- [ ] Final acceptance testing

**Deliverables:**
- Complete README
- Sample data for 3 companies
- All bugs fixed
- System ready for daily use

**Acceptance:**
- New user can follow README and run first simulation in 15 minutes
- All core features work without errors
- Sample scenarios demonstrate capabilities

---

## Phase 9: FastAPI Backend Split (Day 22)

### Goals
- Decouple UI from agent logic for cloud deployment readiness
- Create minimal REST API wrapper (POC-compliant: ~100 lines)
- Enable future external API access
- Maintain local development workflow

### Tasks

#### Day 22: FastAPI Implementation
- [ ] Add dependencies: `fastapi`, `uvicorn[standard]` to pyproject.toml
- [ ] Create `backend/` package structure
- [ ] Implement `backend/main.py` with FastAPI app (~50 lines)
  - `POST /api/conversations/run` - Execute conversation, return full result
  - `GET /api/conversations/{id}` - Get saved conversation from Weaviate
  - `POST /api/agents/suggest` - LLM-based agent suggestion (placeholder)
  - `GET /api/health` - Health check (Ollama, Weaviate, Redis status)
- [ ] Create `backend/models.py` with Pydantic schemas (~50 lines)
  - `ConversationRequest`, `ConversationResponse`, `AgentConfig`, `MessageSchema`
- [ ] Update docker-compose.yml: Add `backend` service (port 8000)
- [ ] Refactor Streamlit app.py to call FastAPI endpoints
  - Replace direct Agent/Orchestrator imports with httpx API client
  - Keep UI rendering logic, remove business logic
- [ ] Update Makefile: Add `make logs-backend`, `make test-api`
- [ ] Test: End-to-end flow through API

**Architecture Change:**
```
Before: Browser → Streamlit (UI + Logic) → Ollama
After:  Browser → Streamlit (UI only) → FastAPI (Logic) → Ollama
```

**Deliverables:**
- Working FastAPI backend with REST endpoints
- Streamlit as pure API client
- OpenAPI documentation at http://localhost:8000/docs
- Cloud-ready API (same code works locally + cloud)

**Acceptance:**
- `curl -X POST http://localhost:8000/api/conversations/run` returns conversation
- Streamlit UI works identically through API
- OpenAPI docs accessible and accurate
- No agent imports in app.py

**POC Compliance:**
- Total new code: ~100 lines (backend/main.py + models.py)
- Modified code: ~50 lines (app.py API client refactor)
- New containers: 1 (backend)
- Timeline: 1 day
- Philosophy: Minimal wrapper, defer complexity (no async workers yet)

---

## Alpha Release Checklist

### Infrastructure
- [x] Docker Compose with 3 services configured
- [ ] Docker Compose with 4 services (+ backend) - Phase 9
- [x] All health checks passing
- [x] Volume mounts for hot-reload and data persistence
- [x] Ollama models downloaded and accessible (llama3.1 confirmed)

### Backend API (Phase 9)
- [ ] FastAPI application created with core endpoints
- [ ] Pydantic models for request/response validation
- [ ] OpenAPI documentation accessible at /docs
- [ ] Health check endpoint functional
- [ ] CORS configured for Streamlit access

### Core Features
- [ ] Document ingestion CLI tool - Not yet implemented
- [ ] Multi-tenant RAG with Weaviate - Not yet implemented
- [x] Agent LLM calls working - Phase 2 complete
- [x] Multi-agent orchestrator - Phase 2 complete
- [ ] LLM-powered scenario generation - Mock implementation only
- [ ] Dynamic agent factory - Not yet implemented

### UI
- [x] Scenario wizard (client, description, participate) - Basic UI implemented
- [x] Agent preview and regeneration - Mock functionality
- [x] Real-time conversation display - UI structure ready
- [ ] Sentiment chart - Placeholder only
- [x] Past conversations tab - UI ready, no data yet
- [x] Human input mode - UI structure ready

### Data & Persistence
- [x] Weaviate collections initialized - Document & ConversationHistory created
- [x] Multi-tenant setup complete - HPE, Toyota, Microsoft tenants active
- [ ] Conversations saved to Weaviate - Not yet implemented
- [ ] JSON exports created - Not yet implemented
- [ ] Sample data for 3 companies - Not yet ingested

### Documentation
- [x] README with setup instructions - Comprehensive documentation
- [x] Business Requirements Document
- [x] Technical Requirements Document
- [x] Implementation Plan (this document)
- [x] UI Specification

### Testing
- [x] 2-agent autonomous conversation works - Phase 2 complete
- [x] 4-agent multi-party conversation works - Phase 2 complete
- [ ] Conversation works through API (Phase 9)
- [ ] OpenAPI schema validates all endpoints (Phase 9)
- [ ] Human participation mode works - UI ready, no backend
- [ ] RAG retrieves correct tenant data - Not yet implemented
- [ ] Sentiment analysis functional - Placeholder only
- [ ] Conversation replay works - UI ready, no backend

---

## Future Phases

### Phase 2: Concurrent Multi-Scenario Execution (Cloud Scalability)

**Timeline:** 8-10 days  
**Priority:** High (when deploying to cloud with concurrent traffic)

**Context:** Phase 9 creates a synchronous API suitable for single-user POC and low-traffic cloud deployments. This phase adds infrastructure for handling **multiple simultaneous conversation requests** from different clients/users.

**When to implement:**
- Deploying to cloud with >5 concurrent users
- Need non-blocking conversation execution
- Multiple API clients making simultaneous requests
- Real-time token streaming required (word-by-word)

**Architecture Evolution:**
```
Phase 9 (Synchronous):  Client → FastAPI → Agent (blocks) → Ollama
Phase 2 (Async):        Client → FastAPI → Redis Queue → Celery Workers → Ollama
                                    ↓                        ↓
                                  SSE Stream ← Redis Pub/Sub ← Tokens
```

**Features:**
- [ ] **Async Task Queue**
  - Add Redis service to docker-compose.yml
  - Install Celery with Redis broker
  - Create `backend/tasks.py` with `run_conversation` Celery task (~80 lines)
  - Worker container executes conversations in background
  - API returns conversation_id immediately, doesn't block

- [ ] **Real-Time Token Streaming**
  - Modify `Agent.respond()` to use Ollama `stream=True` (~30 lines)
  - Parse SSE stream from Ollama, yield tokens
  - Publish tokens to Redis pub/sub channel `conversation:{id}`
  - Create `backend/streaming.py` with SSE endpoint (~100 lines)
  - `GET /api/conversations/{id}/stream` - Server-Sent Events endpoint
  - Frontend consumes SSE stream for word-by-word display

- [ ] **Conversation State Management**
  - Redis as state cache (running conversations, metadata)
  - Weaviate for persistence (completed conversations)
  - `POST /api/conversations/{id}/stop` - Cancel running conversation
  - Handle worker timeout, cleanup, error recovery

- [ ] **Worker Orchestration**
  - Celery worker container (separate from API)
  - Task routing, priority queues
  - Configurable worker count (horizontal scaling)
  - Health monitoring via `celery inspect`

**Infrastructure Changes:**
```yaml
# docker-compose.yml additions
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  worker:
    build: .
    command: celery -A backend.celery_app worker --loglevel=info
    depends_on: [redis, ollama, weaviate]
```

**New Dependencies:**
- `celery[redis] ^5.3.0`
- `redis ^5.0.0`
- `sse-starlette ^1.8.0` (for SSE streaming)

**Code Additions:**
- `backend/celery_app.py`: Celery configuration (~40 lines)
- `backend/tasks.py`: Async conversation task (~80 lines)
- `backend/streaming.py`: SSE streaming logic (~100 lines)
- `src/agents/core.py`: Token streaming support (~30 lines modified)
- `docker-compose.yml`: Redis + worker services (~20 lines)

**Total Complexity:**
- New code: ~250 lines
- Modified code: ~80 lines
- New containers: +2 (redis, worker)
- New dependencies: 3 packages

**Testing Scenarios:**
1. **Concurrent conversations**: 5 clients start conversations simultaneously
2. **Token streaming**: See LLM generate text word-by-word in real-time
3. **Cancellation**: Stop conversation mid-execution, worker cleans up
4. **Reconnection**: Client disconnects, reconnects to ongoing stream
5. **Worker scaling**: Add 3 workers, verify load distribution

**Acceptance Criteria:**
- 10+ concurrent conversations execute without blocking
- Tokens stream to UI within 100ms of generation
- Stop button cancels worker task within 2 seconds
- No memory leaks after 100+ conversations
- Worker crashes don't lose conversation state

**POC vs Production Trade-offs:**
- **Skip for POC if:** Single user, local only, synchronous OK
- **Implement when:** Cloud deployment, multiple users, UX requires real-time streaming
- **Future optimization:** Model quantization, response caching, connection pooling

**Deliverables:**
- Scalable background job execution
- Real-time streaming capability
- Foundation for production deployment
- Handles 50+ concurrent conversations

---

### Phase 3: Enhanced Capabilities (Post-Alpha)

**Timeline:** 2-3 weeks  
**Priority:** Medium

**Features:**
- [ ] Scenario template persistence
  - Save successful configurations as templates
  - Template library in Streamlit sidebar
  - Quick load from templates
  
- [ ] Agent role presets
  - Library of common roles (Sales Engineer, Legal Counsel, etc.)
  - Pre-written system prompts
  - Quick agent creation from presets

- [ ] Advanced sentiment analysis
  - Emotion detection (anger, frustration, satisfaction)
  - Multi-dimensional sentiment (professionalism, engagement, agreement)
  - Sentiment trend prediction

- [ ] Export & sharing
  - Export conversations to PDF
  - Markdown export for documentation
  - Share scenario configs with team

- [ ] Conversation branching
  - Save checkpoints during conversation
  - Restart from checkpoint with different strategy
  - Compare outcomes of different branches

**Deliverables:**
- Reusable scenario library
- Faster agent creation via presets
- Better evaluation capabilities

---

### Phase 4: Advanced Analytics & Evaluation (Post-Alpha)

**Timeline:** 3-4 weeks  
**Priority:** High (for experimental work)

**Features:**
- [ ] Phoenix observability integration
  - Trace every LLM call
  - Visualize agent decision-making
  - Performance profiling per component
  - Debug mode for development

- [ ] MLflow experiment tracking
  - Track scenarios as experiments
  - Compare multiple runs
  - Version agent configurations
  - Metrics dashboard

- [ ] RAGAS evaluation
  - Answer relevancy scoring
  - Faithfulness to source documents
  - Context precision and recall
  - Automated quality assessment

- [ ] A/B testing framework
  - Run same scenario with different models
  - Run same scenario with different prompts
  - Statistical comparison of outcomes
  - Automated report generation

- [ ] Custom metrics
  - Keyword detection (deal keywords, objections)
  - Turn efficiency (outcome per turn count)
  - RAG usage statistics
  - Cost tracking (tokens used)

**Deliverables:**
- Comprehensive evaluation framework
- Experiment comparison tools
- Data-driven decision making

---

### Phase 5: Collaboration & Sharing (Future)

**Timeline:** 4-5 weeks  
**Priority:** Low (unless team adoption high)

**Features:**
- [ ] Multi-user support
  - User authentication
  - Personal conversation history
  - Shared vs private scenarios

- [ ] Team features
  - Shared scenario library
  - Collaborative editing
  - Comments and annotations
  - Performance leaderboards

- [ ] API enhancements
  - Webhook support for conversation events
  - Programmatic scenario creation endpoints
  - Bulk operations API
  - GraphQL interface (alternative to REST)

**Deliverables:**
- Multi-user platform
- Team collaboration tools
- External integration capabilities

---

### Phase 6: Production Hardening (Future)

**Timeline:** 6-8 weeks  
**Priority:** Low (only if productionizing)

**Features:**
- [ ] Kubernetes deployment
  - Helm charts
  - Auto-scaling
  - Load balancing
  - Rolling updates

- [ ] Security hardening
  - OAuth 2.0 authentication
  - Role-based access control (RBAC)
  - Data encryption at rest and in transit
  - Secrets management (Vault)
  - Input validation and sanitization

- [ ] Monitoring & observability
  - Prometheus metrics
  - Grafana dashboards
  - ELK stack for logging
  - Alerting (PagerDuty, Slack)

- [ ] Performance optimization
  - Model quantization (4-bit, 8-bit)
  - Response caching (Redis)
  - Connection pooling
  - Horizontal scaling

- [ ] CI/CD pipeline
  - GitHub Actions workflows
  - Automated testing
  - Docker image building
  - Deployment automation

- [ ] Disaster recovery
  - Automated backups
  - Point-in-time recovery
  - Multi-region deployment
  - Failover mechanisms

**Deliverables:**
- Production-grade platform
- Enterprise security
- High availability
- Automated operations

---

### Phase 7: Advanced Features (Future)

**Timeline:** Variable  
**Priority:** As needed

**Potential Features:**
- [ ] Multi-modal agents (vision, audio)
- [ ] Real-time voice conversations
- [ ] Integration with external systems (CRM, email)
- [ ] Automated scenario generation from recordings
- [ ] Multi-language support
- [ ] Agent learning from feedback
- [ ] Reinforcement learning for optimization
- [ ] Blockchain for conversation immutability
- [ ] VR/AR visualization of conversations

---

## Risk Management

### High-Priority Risks

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| LLM responses too slow | High | Use smaller models, optimize prompts, cache responses | Developer |
| Weaviate memory overflow | Medium | Limit ingestion, document cleanup procedures | Developer |
| Docker resource exhaustion | High | Document requirements, set resource limits | Developer |
| Scope creep in Alpha | High | Strict adherence to checklist, defer extras to Phase 2+ | Developer |
| API-UI coupling issues | Medium | Clear Pydantic contracts, comprehensive testing | Developer |
| Premature optimization | High | Follow POC philosophy, add complexity only when needed | Developer |

### Dependencies

| Dependency | Status | Risk Level | Backup Plan |
|------------|--------|------------|-------------|
| Ollama API stability | Active development | Medium | Switch to vLLM or llama.cpp |
| Weaviate multi-tenancy | Stable (v1.24+) | Low | Fall back to collection-per-tenant |
| LlamaIndex compatibility | Active development | Medium | Custom RAG implementation |
| Streamlit limitations | Stable | Low | Migrate to Gradio if needed |
| FastAPI ecosystem | Stable | Low | Flask alternative (simpler but less features) |
| Celery + Redis (future) | Mature | Low | RQ (simpler) or serverless functions |

---

## Success Metrics

### Alpha Success Criteria

**Functionality:**
- 100% of core features working (scenario creation, conversation, persistence)
- < 5% failure rate on agent generation
- < 2% data loss on conversation save
- API endpoints return valid responses with correct schemas

**Performance:**
- Setup time < 15 minutes (fresh install)
- Scenario creation < 5 minutes
- Agent response time < 10 seconds (95th percentile)
- API response time < 200ms overhead (excluding LLM)

**Usability:**
- First-time user can run simulation without help
- < 3 clicks to start conversation
- Clear error messages for common issues
- OpenAPI documentation accurate and complete

**Quality:**
- Agents respond coherently (manual evaluation)
- RAG retrieves relevant data (>80% accuracy)
- Sentiment scores correlate with message tone
- API contracts validated with Pydantic

---

## Resource Requirements

### Development Time
- **Alpha (Phases 1-9):** 22 days (~4 weeks)
  - Core functionality: 21 days
  - FastAPI backend split: 1 day
- **Future Phase 2 (Scalability):** 8-10 days (when needed)
- **Future Phase 3 (Enhanced Capabilities):** 14 days (2-3 weeks)
- **Future Phase 4 (Analytics):** 21 days (3-4 weeks)
- **Total to full-featured:** ~2-3 months

### Hardware
- **Development (Local POC):**
  - 8+ CPU cores, 16GB RAM
  - 50GB free disk (models and data)
  
- **Cloud Deployment (Future):**
  - Backend API: 2 vCPU, 4GB RAM (Cloud Run, Lambda, ECS)
  - Ollama: GPU instance (T4/A10, 16GB VRAM) or CPU optimized
  - Weaviate: Managed service or 4GB RAM instance
  - Redis: Managed service or 1GB RAM (if using workers)

### External Resources
- None (fully local)

---

## Communication Plan

### Internal Updates (Self)
- Daily progress log in project notes
- Weekly review of completed vs planned tasks
- Adjust timeline based on actual progress

### If Sharing with Team
- Weekly demo of new features
- Slack updates on milestones
- Request feedback after Alpha release

---

## Appendix

### A. Project Directory Structure (Final State)

```
callisto/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── README.md
├── .dockerignore
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── backend/                    # NEW (Phase 9)
│   ├── __init__.py
│   ├── main.py                 # FastAPI app (~50 lines)
│   └── models.py               # Pydantic schemas (~50 lines)
│
├── src/
│   ├── __init__.py
│   ├── app.py                  # Streamlit UI (API client after Phase 9)
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── core.py             # Agent, HumanAgent, Orchestrator
│   │   ├── factory.py          # Dynamic agent generation
│   │   └── suggester.py        # LLM scenario wizard
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── index.py            # LlamaIndex setup
│   │   └── retrieval.py        # RAG tools
│   │
│   └── utils/
│       ├── __init__.py
│       ├── persistence.py      # Save/load conversations
│       └── tenants.py          # Tenant management
│
├── scripts/
│   ├── init_weaviate.py       # Initialize collections
│   └── ingest_documents.py    # Document ingestion CLI
│
├── data/
│   ├── conversations/          # JSON exports
│   └── documents/              # Input documents
│       ├── hpe/
│       ├── toyota/
│       └── microsoft/
│
└── documentation/              # Documentation
    ├── Business Requirements Document - Callisto.md
    ├── Technical Requirements Document - Callisto.md
    ├── Implementation Plan - Callisto.md (this file)
    └── UI Specification - Callisto.md
```

### B. Command Reference

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app          # Frontend (Streamlit)
docker-compose logs -f backend      # Backend (FastAPI) - Phase 9+
docker-compose logs -f worker       # Worker (Celery) - Future Phase 2+

# Stop services
docker-compose down

# Rebuild after dependency changes
docker-compose build app
docker-compose build backend  # Phase 9+

# Pull Ollama models
docker-compose exec ollama ollama pull llama3.1
docker-compose exec ollama ollama pull nomic-embed-text

# Initialize Weaviate
docker-compose exec app python scripts/init_weaviate.py

# Ingest documents
docker-compose exec app python scripts/ingest_documents.py \
  --company "HPE" --path /app/data/documents/hpe/

# Test API (Phase 9+)
curl http://localhost:8000/health
curl http://localhost:8000/docs  # OpenAPI documentation

# Access services
# Streamlit: http://localhost:8501
# FastAPI: http://localhost:8000 (Phase 9+)
# Weaviate: http://localhost:8080
# Ollama: http://localhost:11434
```

### C. Timeline Visualization

```
Week 1: Foundation
├── Day 1-3: Infrastructure ✅
└── Day 4-6: Agent Core & LLM Integration ✅

Week 2: Core Features
├── Day 7-9: LLM Scenario Generation
├── Day 10-12: RAG Pipeline
└── Day 13-15: UI Development

Week 3: Completion
├── Day 16-17: Persistence
├── Day 18-19: Human Mode
└── Day 20-21: Polish & Docs

Week 4: Cloud-Ready Architecture
└── Day 22: FastAPI Backend Split (Phase 9)

Alpha Release: Day 22 ✓

Future (When Needed):
└── Concurrent Multi-Scenario Execution (~8-10 days)
    ├── Async task queue (Celery + Redis)
    ├── Real-time token streaming (SSE)
    └── Worker orchestration
```
