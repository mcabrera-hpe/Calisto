# Business Requirements Document - Callisto

**Project:** Multi-Agent Conversation Simulator for PoC Development  
**Author:** Senior AI/ML Engineer  
**Date:** January 30, 2026  
**Version:** Alpha

---

## 1. Executive Summary

### 1.1 Purpose
Create a standardized, reusable platform for rapidly building and testing AI agent-based PoCs, specifically focusing on multi-agent conversation simulations between different companies (B2B scenarios).

### 1.2 Problem Statement
As a Senior AI/ML engineer constantly building PoCs, current challenges include:
- **Repetitive scaffolding** - Each agent PoC requires rebuilding similar infrastructure
- **Inconsistent tools** - No standardized stack leads to different approaches each time
- **Time-consuming setup** - Setting up LLMs, vector databases, and RAG pipelines takes hours
- **Limited reusability** - Hard to compare different approaches or models systematically
- **Complex multi-agent orchestration** - No easy way to simulate multi-party conversations

### 1.3 Solution
Build "Callisto" - a Dockerized platform that:
- Provides standardized agent infrastructure (LLM, vector DB, RAG)
- Enables dynamic scenario creation through LLM-powered wizards
- Supports both autonomous agent simulations and human participation
- Allows rapid experimentation with different models and strategies
- Runs 100% locally with no cloud dependencies

---

## 2. Business Objectives

### 2.1 Primary Goals
1. **Reduce PoC Development Time**: From days to hours for standard agent scenarios
2. **Enable Rapid Experimentation**: Easy comparison of different LLMs, prompts, and strategies
3. **Standardize Tooling**: Consistent stack across all agent-based PoCs
4. **Support Learning**: Understand client perspectives by simulating their agents

### 2.2 Success Metrics
- **Setup Time**: < 15 minutes from git clone to running simulation
- **Scenario Creation**: < 5 minutes to create and run new scenario
- **Reusability**: 80% of code shared across different PoC types
- **Iteration Speed**: Test 10+ scenario variations in one day

### 2.3 Out of Scope (Alpha)
- Production deployment or scaling
- External stakeholder demos (internal use only)
- Multi-modal agents (text-only)
- Real-time integrations with external systems
- Advanced observability (Phoenix - moved to future phases)
- Experiment tracking at scale (MLflow - moved to future phases)

---

## 3. User Needs

### 3.1 Primary User
**Role:** Senior AI/ML Engineer (myself)  
**Context:** Building PoCs to explore AI agent capabilities and validate approaches

### 3.2 Use Cases

#### UC1: Simulate B2B Sales Conversation
**Goal:** Test how an AI sales agent performs against a simulated client  
**Flow:**
1. Select client company (e.g., Toyota)
2. Describe scenario: "Negotiate server purchase contract"
3. System generates 2 agents (HPE sales, Toyota procurement)
4. Run autonomous simulation
5. Analyze sentiment progression and outcome

#### UC2: Practice Client Interaction
**Goal:** Prepare for real client meeting by practicing with simulated agent  
**Flow:**
1. Select client company
2. Describe scenario: "Discuss contract renewal concerns"
3. Check "I want to participate"
4. System generates client agent with real company data
5. Have conversation with AI client
6. Review performance and refine approach

#### UC3: Multi-Party Enterprise Deal
**Goal:** Simulate complex 4-way negotiation  
**Flow:**
1. Describe scenario: "Enterprise deal with technical and legal stakeholders"
2. System suggests 4 agents (HPE sales + tech, Client procurement + legal)
3. Run simulation
4. Analyze how technical and legal concerns were addressed

#### UC4: Compare Model Performance
**Goal:** Test which LLM works best for sales scenarios  
**Flow:**
1. Create scenario once
2. Run with Llama 3.1
3. Run same scenario with Mistral
4. Compare sentiment, turns taken, outcome achieved
5. Save both conversations for analysis

#### UC5: Test Different Strategies
**Goal:** Validate which negotiation approach works better  
**Flow:**
1. Same scenario, different agent prompts
2. Version A: Aggressive pricing strategy
3. Version B: Relationship-focused approach
4. Compare final client sentiment and deal closure

---

## 4. Functional Requirements

### 4.1 Core Features (Alpha - Must Have)

#### F1: Dynamic Scenario Creation
- **Input:** Client company + scenario description (natural language)
- **Output:** Complete agent configuration (names, companies, roles, objectives)
- **Method:** LLM-powered suggestion with few-shot examples
- **User Control:** Preview and regenerate if needed

#### F2: Multi-Tenant Knowledge Base
- **Capability:** Each company has isolated document store
- **Implementation:** Weaviate multi-tenancy (one tenant per company)
- **Access Control:** Agents only query their company's tenant
- **Example:** HPE agent accesses HPE docs, Toyota agent accesses Toyota docs

#### F3: Agent Orchestration
- **Support:** 2-6 agents per conversation
- **Modes:** Autonomous (agents only) or Interactive (human participates)
- **Turn Management:** Round-robin with skip logic
- **Termination:** Max turns (30) or sentiment threshold

#### F4: Real-Time Sentiment Analysis
- **Tracking:** Per-turn sentiment for each side (company vs client)
- **Display:** Live chart showing sentiment progression
- **Model:** Transformers (distilbert) running locally

#### F5: Conversation Persistence
- **Storage:** Weaviate (searchable) + JSON exports (backup)
- **Content:** Full conversation + agent configs + generated prompts
- **Replay:** Load and view past conversations
- **Purpose:** Reproducibility and analysis

#### F6: RAG Pipeline
- **Document Loading:** PDF, DOCX, text files
- **Chunking:** Semantic chunking via LlamaIndex
- **Embeddings:** Ollama (nomic-embed-text)
- **Retrieval:** Top-K similarity search per tenant

#### F7: Data Ingestion
- **CLI Tool:** `ingest_documents.py --company <name> --path <dir>`
- **Processing:** Auto-chunk, embed, store in Weaviate
- **Tenant Management:** Auto-create if doesn't exist (with warning)

### 4.2 UI Requirements

#### UI1: Scenario Wizard (Sidebar)
- Client dropdown (auto-populated from Weaviate tenants)
- Scenario description textarea
- "I want to participate" checkbox
- "Generate Agents" button
- Agent preview with "Run" and "Regenerate" buttons

#### UI2: Conversation View
- Chat-style interface with agent names and companies
- Clear visual distinction (company side vs client side)
- Real-time message streaming
- Sentiment chart (line graph)
- Turn counter

#### UI3: Past Conversations
- Filterable list (by client, date)
- Conversation replay
- Metrics summary (turns, sentiment, outcome)
- Export button

### 4.3 Technical Capabilities

#### T1: Hot-Reload Development
- Code changes in `src/` auto-reload in Streamlit
- No container rebuild required
- Fast iteration during development

#### T2: Local Execution
- All processing on local machine
- No external API calls
- No cloud dependencies
- Works offline

#### T3: Streaming LLM Responses
- Real-time token streaming from Ollama
- Progressive UI updates
- Better user experience vs waiting for full response

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Scenario Generation:** < 10 seconds to generate agent configs
- **Agent Response:** < 5 seconds per turn (without RAG)
- **RAG Query:** < 3 seconds for retrieval
- **Ingestion:** Process 100 pages in < 2 minutes

### 5.2 Usability
- **Setup:** Non-expert should get system running in 15 minutes
- **Scenario Creation:** Intuitive wizard, minimal fields
- **Error Messages:** Clear guidance when something fails

### 5.3 Reliability
- **Container Health:** Auto-restart on crash
- **Graceful Degradation:** Handle missing Ollama models
- **Data Persistence:** Conversations survive container restarts

### 5.4 Maintainability
- **Code Organization:** Clear module separation
- **Documentation:** README with setup steps
- **Dependencies:** Poetry lock file for reproducibility

---

## 6. Data Requirements

### 6.1 Input Data
- **Company Documents:** PDF, DOCX files (product specs, pricing, policies)
- **Volume:** 10-100 documents per company
- **Size:** Up to 1000 pages total per tenant

### 6.2 Generated Data
- **Conversations:** JSON exports (~10-50KB each)
- **Weaviate Storage:** Vectors + metadata (~100MB per 10k chunks)
- **Retention:** Keep all for analysis (no auto-cleanup in Alpha)

### 6.3 Sample Data (Included)
- HPE: Product catalogs, pricing guides, technical specs
- Toyota: Procurement policies, contract templates
- Microsoft: Sample enterprise customer data

---

## 7. Constraints & Assumptions

### 7.1 Constraints
- **Local Resources:** Limited by laptop CPU/RAM (no GPU required but helpful)
- **Model Size:** Use models that fit in 16GB RAM (Llama 3.1 8B, not 70B)
- **Budget:** $0 - no paid services
- **Timeline:** Alpha in 2-3 weeks

### 7.2 Assumptions
- User has Docker installed and working
- User comfortable with command line
- Documents in English (no i18n needed)
- User understands AI limitations (hallucinations, etc.)

---

## 8. Dependencies & Integrations

### 8.1 External Dependencies
- **Ollama:** For LLM inference and embeddings
- **Weaviate:** For vector storage
- **HuggingFace Models:** For sentiment analysis (transformers)

### 8.2 No Integrations (Alpha)
- No external APIs
- No databases beyond Weaviate
- No authentication/authorization
- No real client systems

---

## 9. Risks & Mitigations

### 9.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Ollama too slow on laptop | High | Medium | Use smaller models, optimize prompts |
| Weaviate memory overflow | Medium | Low | Limit document ingestion, cleanup old data |
| LLM hallucinations in agents | Medium | High | Add grounding via RAG, include disclaimers |
| Docker resource exhaustion | High | Low | Document minimum requirements, add limits |

### 9.2 Scope Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Feature creep | High | Strict Alpha scope, move extras to Future Phases |
| Over-engineering | Medium | Start simple, iterate based on usage |
| Unclear requirements | Medium | This document clarifies needs |

---

## 10. Future Phases (Post-Alpha)

### Phase 2: Enhanced Capabilities
- Scenario template persistence (save/reuse configs)
- Agent role presets library
- Multi-language support
- Voice integration (text-to-speech)

### Phase 3: Advanced Analytics
- Phoenix observability (detailed tracing)
- MLflow experiment tracking
- RAGAS evaluation metrics
- A/B testing framework

### Phase 4: Collaboration
- Multi-user support
- Shared scenario library
- Team performance leaderboards
- Export to presentation format

### Phase 5: Production Readiness
- Authentication & authorization
- Cloud deployment option
- API for external integrations
- Performance optimization at scale

---

## 11. Acceptance Criteria

### Alpha Release Ready When:
- ✅ User can create scenario via wizard in < 5 minutes
- ✅ System generates appropriate agents from description
- ✅ Autonomous 2-agent conversation runs successfully
- ✅ Human can participate in conversation
- ✅ Sentiment chart updates in real-time
- ✅ Conversations saved and retrievable
- ✅ RAG retrieves relevant company-specific data
- ✅ Setup documentation enables first-time setup in 15 min
- ✅ At least 2 sample companies with data included
- ✅ All services run in Docker Compose

---

## 12. Glossary

**Agent:** AI entity representing a person/role in conversation  
**Tenant:** Weaviate multi-tenancy unit, one per company  
**RAG:** Retrieval-Augmented Generation (search then generate)  
**Scenario:** Configuration defining conversation objective and participants  
**Orchestrator:** Code managing turn-taking between agents  
**LLM:** Large Language Model (e.g., Llama 3.1)  
**Embedding:** Vector representation of text for similarity search  
**Sentiment:** Positive/negative emotional tone (0-1 scale)
