# Callisto - Implementation Plan

**Project:** Multi-Agent Conversation Simulator  
**Version:** Alpha  
**Date:** January 30, 2026 (Updated: February 2, 2026)  
**Timeline:** 2-3 weeks

---

## Current Status (Updated: February 2, 2026)

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
  
### 🚧 In Progress
- **Phase 2 (Days 4-6):** RAG Pipeline - Ready to start
- **Phase 3 (Days 7-9):** Agent Core - Not started

### 📋 Next Steps
1. **Phase 2 (Days 4-6): Agent Core & LLM Integration** - Start here!
   - Build Agent base class with Ollama integration
   - Implement conversation orchestrator
   - Connect to UI for real conversations
2. Phase 3 (Days 7-9): LLM-Powered Scenario Generation
3. Phase 4 (Days 10-12): RAG Pipeline (defer until agents working)

### 📊 Overall Progress: ~20% Complete
- Infrastructure: 100% ✅
- Core Features: 5%
- UI Framework: 40%
- Documentation: 100%

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

## Phase 2: Agent Core & LLM Integration (Days 4-6) 🚀 CURRENT PHASE

### Goals
- Build agent classes and orchestration
- Implement direct Ollama calls
- Get agents talking to each other autonomously
- **Skip RAG for now** - agents can talk without external data

### Tasks

#### Day 4: Agent Base Class
- [ ] Create `src/agents/core.py` with simple Agent class
- [ ] Implement `Agent.respond()` with direct Ollama HTTP calls
- [ ] Test: Single agent responds to a message
- [ ] Add basic system prompt support

#### Day 5: Orchestrator & Multi-Turn
- [ ] Implement `MultiAgentOrchestrator` class in `core.py`
- [ ] Add round-robin turn management
- [ ] Implement conversation history tracking
- [ ] Test: 2 agents have a 5-turn conversation (command line test)

#### Day 6: UI Integration
- [ ] Connect orchestrator to Streamlit UI
- [ ] Replace mock agent generation with real agent creation
- [ ] Implement auto-run conversation when user clicks "Run Simulation"
- [ ] Add streaming display (optional - can be basic first)
- [ ] Test: End-to-end UI flow with real agent conversation

**Deliverables:**
- Working Agent class with LLM integration
- Basic orchestration for multi-turn conversations
- Agents conversing in the UI

**Acceptance:**
- Create 2 agents via UI, click "Run Simulation"
- Agents respond coherently using Ollama
- Conversation completes without errors
- Messages display in UI in real-time

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

## Alpha Release Checklist

### Infrastructure
- [x] Docker Compose with 3 services configured
- [x] All health checks passing
- [x] Volume mounts for hot-reload and data persistence
- [x] Ollama models downloaded and accessible (llama3.1 confirmed)

### Core Features
- [ ] Document ingestion CLI tool - Not yet implemented
- [ ] Multi-tenant RAG with Weaviate - Not yet implemented
- [ ] Agent LLM calls with streaming - Not yet implemented
- [ ] Multi-agent orchestrator - Not yet implemented
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
- [ ] 2-agent autonomous conversation works - Not yet testable
- [ ] 4-agent multi-party conversation works - Not yet testable
- [ ] Human participation mode works - UI ready, no backend
- [ ] RAG retrieves correct tenant data - Not yet implemented
- [ ] Sentiment analysis functional - Placeholder only
- [ ] Conversation replay works - UI ready, no backend

---

## Future Phases

### Phase 2: Enhanced Capabilities (Post-Alpha)

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

### Phase 3: Advanced Analytics & Evaluation (Post-Alpha)

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

### Phase 4: Collaboration & Sharing (Future)

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

- [ ] API development
  - REST API for external integrations
  - Webhook support
  - Programmatic scenario creation
  - Bulk operations

- [ ] Advanced UI
  - React/Next.js frontend (replace Streamlit)
  - Mobile-responsive design
  - Dark mode
  - Customizable dashboards

**Deliverables:**
- Multi-user platform
- Team collaboration tools
- External integration capabilities

---

### Phase 5: Production Hardening (Future)

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

### Phase 6: Advanced Features (Future)

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

### Dependencies

| Dependency | Status | Risk Level | Backup Plan |
|------------|--------|------------|-------------|
| Ollama API stability | Active development | Medium | Switch to vLLM or llama.cpp |
| Weaviate multi-tenancy | Stable (v1.24+) | Low | Fall back to collection-per-tenant |
| LlamaIndex compatibility | Active development | Medium | Custom RAG implementation |
| Streamlit limitations | Stable | Low | Migrate to Gradio if needed |

---

## Success Metrics

### Alpha Success Criteria

**Functionality:**
- 100% of core features working (scenario creation, conversation, persistence)
- < 5% failure rate on agent generation
- < 2% data loss on conversation save

**Performance:**
- Setup time < 15 minutes (fresh install)
- Scenario creation < 5 minutes
- Agent response time < 10 seconds (95th percentile)

**Usability:**
- First-time user can run simulation without help
- < 3 clicks to start conversation
- Clear error messages for common issues

**Quality:**
- Agents respond coherently (manual evaluation)
- RAG retrieves relevant data (>80% accuracy)
- Sentiment scores correlate with message tone

---

## Resource Requirements

### Development Time
- **Alpha (Phases 1-8):** 21 days (~3 weeks)
- **Phase 2:** 14 days (2-3 weeks)
- **Phase 3:** 21 days (3-4 weeks)
- **Total to full-featured:** ~2-3 months

### Hardware
- Development laptop: 8+ cores, 16GB RAM
- Disk: 50GB free (for models and data)

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
├── docker-compose.dev.yml
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
├── src/
│   ├── __init__.py
│   ├── app.py                  # Streamlit UI
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
└── docs/                       # Documentation
    ├── Business Requirements Document.md
    ├── Technical Requirements Document.md
    └── Implementation Plan.md (this file)
```

### B. Command Reference

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild after dependency changes
docker-compose build app

# Pull Ollama models
docker-compose exec ollama ollama pull llama3.1
docker-compose exec ollama ollama pull nomic-embed-text

# Initialize Weaviate
docker-compose exec app python scripts/init_weaviate.py

# Ingest documents
docker-compose exec app python scripts/ingest_documents.py \
  --company "HPE" --path /app/data/documents/hpe/

# Access services
# Streamlit: http://localhost:8501
# Weaviate: http://localhost:8080
# Ollama: http://localhost:11434
```

### C. Timeline Visualization

```
Week 1: Foundation
├── Day 1-3: Infrastructure
└── Day 4-6: RAG Pipeline

Week 2: Core Features
├── Day 7-9: Agent System
├── Day 10-12: Scenario Generation
└── Day 13-15: UI Development

Week 3: Completion
├── Day 16-17: Persistence
├── Day 18-19: Human Mode
└── Day 20-21: Polish & Docs

Alpha Release: Day 21 ✓
```
