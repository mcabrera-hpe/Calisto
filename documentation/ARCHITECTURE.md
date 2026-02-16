# Callisto Architecture Quick Reference

**Last Updated:** February 13, 2026  
**Purpose:** Fast context-loading for AI agents and developers

---

## 🏗️ System Architecture

```
┌─────────────┐      HTTP/SSE        ┌──────────────┐
│  Streamlit  │ ──────────────────► │   FastAPI    │
│  UI (8501)  │                      │  API (8000)  │
└─────────────┘                      └──────┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Orchestrator  │
                                    │  (Round-robin)│
                                    └───────┬───────┘
                                            │
                                            ▼
                              ┌─────────────────────────┐
                              │   Agent   │   Agent     │
                              │  (HPE)    │  (Client)   │
                              └─────┬─────┴─────┬───────┘
                                    │           │
                                    ▼           ▼
                              ┌─────────────────────────┐
                              │  Proxy (host:7000)      │
                              │  proxy_server.py        │
                              └───────────┬─────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ External LLM API │
                                │ (via VPN)        │
                                └──────────────────┘

┌──────────────┐
│  Weaviate    │  (Ready for RAG, not yet integrated)
│  (8080)      │
└──────────────┘
```

---

## 📁 Core Components

### **Agent System** ([src/agents/](../src/agents/))

**[base.py](../src/agents/base.py)** - Agent and HumanAgent classes
- **Key Pattern**: `respond(history) -> tuple[str, float]` (message, generation_time)
- **LLM Integration**: Calls external API with OpenAI format
- **System Prompts**: Dynamically generated from name/company/role/objective
- **Error Handling**: Fail fast with timeout (60s), connection errors logged

**[orchestrator.py](../src/agents/orchestrator.py)** - MultiAgentOrchestrator
- **Round-robin**: Agents take turns sequentially
- **Dual Modes**:
  - `run()` - Returns full conversation history (batch)
  - `run_streaming()` - Generator for real-time UI updates (SSE)
- **Termination**: Keyword detection ("deal", "agreed", "contract")
- **History**: Shared context across all agents

**[core.py](../src/agents/core.py)** - Re-exports for backwards compatibility
- Imports from `base.py` and `orchestrator.py`

### **API Layer** ([src/api/](../src/api/))

**[main.py](../src/api/main.py)** - FastAPI REST backend
- **POST /conversations** - Create conversation, returns UUID
- **GET /conversations/{id}** - Retrieve details
- **POST /conversations/{id}/start** - Start streaming via SSE
- **DELETE /conversations/{id}** - Delete conversation
- **Storage**: In-memory dict (POC - resets on restart)

**[helpers.py](../src/api/helpers.py)** - Agent factory
- **Current**: Hardcoded 5 agents (HPE sales vs client procurement/technical/finance)
- **Future**: LLM-powered generation (Phase 3, not implemented)

**[models.py](../src/api/models.py)** - Pydantic schemas
- `ConversationRequest` / `ConversationResponse`

### **UI Layer** ([src/ui/](../src/ui/))

**[main.py](../src/ui/main.py)** - Streamlit interface
- **Scenario wizard**: Client, scenario text, max turns, num agents
- **Real-time streaming**: Consumes SSE from API
- **SSE Format**: `data: {json}\n\n`
- **Controls**: Start, stop, restart conversation

### **Utilities** ([src/utils/](../src/utils/))

**[config.py](../src/utils/config.py)** - Centralized environment variables
- `LLM_API_ENDPOINT` - Default: `http://host.docker.internal:7000/v1/chat/completions`
- `LLM_API_TOKEN` - Bearer token for API auth
- `DEFAULT_MODEL` - LLM model name (e.g., `meta/llama-3.1-8b-instruct`)
- `WEAVIATE_URL` - Vector database URL
- `MAX_TURNS` - Conversation limit

**[logging_config.py](../src/utils/logging_config.py)** - Shared logging setup

### **RAG Pipeline** ([src/rag/](../src/rag/))
- **Status**: Empty (Phase 4 not started)
- **Planned**: LlamaIndex + Weaviate multi-tenant retrieval

---

## 🔄 Data Flow

### **Conversation Creation**
1. User fills scenario in Streamlit UI
2. UI → `POST /conversations` → API
3. API stores config in memory, returns `conversation_id`

### **Conversation Streaming**
1. UI → `POST /conversations/{id}/start` → API
2. API creates agents via `create_agent()` factory
3. API creates `MultiAgentOrchestrator(agents, max_turns)`
4. API calls `orchestrator.run_streaming(initial_message)`
5. For each turn:
   - Agent calls `_build_messages(history)` → OpenAI format
   - Agent → Proxy (`host.docker.internal:7000`) → VPN → External LLM
   - LLM response parsed, appended to history
   - Message yielded to API → SSE → UI
6. UI displays messages in real-time

### **Network Path for LLM Calls**
```
Docker Container → host.docker.internal:7000 
                → Flask proxy (proxy_server.py on host)
                → VPN tunnel
                → External LLM API
                → Response back through same path
```

**Why Proxy?** VPN routing requires host network stack - Docker can't connect directly.

---

## 📊 Implementation Status

**Overall Progress:** ~40% Complete (as of Feb 13, 2026)

### ✅ **Completed**
- **Phase 1-2**: Infrastructure, Docker, agent classes, orchestrator, streaming
- **Phase 9**: FastAPI backend split, SSE streaming, API/UI separation
- **Code Quality**: 92.5/100 (Grade A)

### ❌ **Not Implemented**
- **Phase 3**: LLM-powered agent generation (uses hardcoded `api/helpers.py`)
- **Phase 4**: RAG pipeline (`src/rag/` is empty)
- **Persistence**: In-memory only (no database saves)
- **Sentiment Analysis**: Not started
- **Human-in-Loop**: `HumanAgent` class is placeholder only

---

## 🎯 Key Design Patterns

### **1. POC Philosophy - Simplicity First**
- Minimal error handling (fail fast, log errors)
- No retry logic, caching, or complex recovery
- In-memory storage instead of persistence
- Simple keyword matching for termination
- **10 clever lines > 50 robust lines**

### **2. Type Hints & Docstrings (100% Coverage)**
```python
def respond(self, conversation_history: List[Dict]) -> tuple[str, float]:
    """Generate a response based on conversation history.
    
    Args:
        conversation_history: List of messages with 'agent' and 'message' keys
        
    Returns:
        Tuple of (response message, generation time in seconds)
    """
```

### **3. Tuple Return Pattern**
All agents follow this signature:
```python
message, generation_time = agent.respond(history)
```

### **4. Centralized Configuration**
All environment variables in [src/utils/config.py](../src/utils/config.py):
```python
LLM_API_ENDPOINT = os.getenv("LLM_API_ENDPOINT", "...")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "meta/llama-3.1-8b-instruct")
```

### **5. Separation of Concerns**
- **Backend**: `src/api/` - REST endpoints, business logic
- **Frontend**: `src/ui/` - Streamlit display, user input
- **Agents**: `src/agents/` - AI logic, LLM calls
- **Utils**: `src/utils/` - Shared config, logging

---

## 🛠️ Development Workflow

### **Common Commands**
```bash
# Start everything (proxy + containers)
make up

# View logs
make logs-app        # Frontend only
make logs-api        # Backend only
make logs            # All services

# Restart after code changes
make restart

# Stop everything
make down

# Test
./run_tests.sh
docker-compose exec app python scripts/test_agents.py
```

### **Testing**
```bash
# Test proxy
curl http://localhost:7000/health

# Test API
curl http://localhost:8000/
curl -X POST http://localhost:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{"scenario":"Test","client":"Toyota","num_agents":2,"max_turns":2}'

# Access UI
open http://localhost:8501
```

### **Code Changes**
- **No rebuild needed**: Docker volumes auto-sync
- **Restart required**: `make restart` to reload Python modules
- **Log monitoring**: `make logs-app` or `make logs-api`

---

## 🔍 Quick Reference

### **Agent Creation**
```python
from agents import Agent
agent = Agent(name="Sarah", company="HPE", role="Sales Engineer", 
              objective="Sell servers", model=DEFAULT_MODEL)
message, time = agent.respond(conversation_history)
```

### **Orchestrator Usage**
```python
from agents import MultiAgentOrchestrator
orchestrator = MultiAgentOrchestrator(agents, max_turns=10)

# Batch mode
history = orchestrator.run(initial_message="Hello")

# Streaming mode (for SSE)
for msg in orchestrator.run_streaming(initial_message="Hello"):
    yield f"data: {json.dumps(msg)}\n\n"
```

### **API Call from UI**
```python
# Create conversation
response = requests.post(f"{API_URL}/conversations", json={
    "scenario": "Server negotiation",
    "client": "Toyota",
    "num_agents": 2,
    "max_turns": 5
})
conv_id = response.json()["conversation_id"]

# Stream conversation
stream = requests.post(f"{API_URL}/conversations/{conv_id}/start", stream=True)
for line in stream.iter_lines():
    if line.startswith(b'data: '):
        message = json.loads(line[6:])
```

---

## 📚 Critical Documentation

Always check these files for context:
- **[.github/copilot-instructions.md](../.github/copilot-instructions.md)** - Development guidelines, conventions
- **[Implementation Plan - Callisto.md](Implementation%20Plan%20-%20Callisto.md)** - Roadmap, feature status
- **[ProjectScore.md](ProjectScore.md)** - Quality metrics, improvement history
- **[docker-compose.yml](../docker-compose.yml)** - Service definitions
- **[pyproject.toml](../pyproject.toml)** - Dependencies

---

## 💡 Next Development Priorities

1. **LLM Agent Generation** (Phase 3) - Replace hardcoded factory with LLM-powered `suggest_agents_llm()`
2. **RAG Pipeline** (Phase 4) - Integrate LlamaIndex + Weaviate for document retrieval
3. **Persistence** - Save conversations to Weaviate + JSON exports
4. **Human-in-Loop** - Connect `HumanAgent` to Streamlit `chat_input()`

---

**Quick Start for AI Agents:**  
1. Read this file first (2 minutes)
2. Check [Implementation Plan](Implementation%20Plan%20-%20Callisto.md) for current status
3. Review [.github/copilot-instructions.md](../.github/copilot-instructions.md) for coding conventions
4. Start coding! 🚀
