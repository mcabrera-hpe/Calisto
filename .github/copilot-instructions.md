# Callisto Project Guidelines

## Overview
Callisto is a **Dockerized multi-agent conversation simulator** for B2B PoC development. Agents use local Ollama LLMs to simulate business negotiations (e.g., HPE sales vs Toyota procurement). Architecture: 3 containers (app, ollama, weaviate) with Streamlit UI.

**Development Philosophy**: This is a POC with incremental development. Simplicity and minimal code win over completeness. Features are intentionally incomplete - implement what's needed, when it's needed. Clever, concise solutions preferred over robust, production-ready code.

## Code Style

### Python Conventions
- **Type hints required**: All function signatures must include parameter and return types
- **Docstrings**: Google-style docstrings for all classes and public methods
- **Logging over print**: Use `logging.getLogger(__name__)` with INFO/ERROR levels
- **Minimal over robust**: Prefer simple, clever implementations - see [src/agents/core.py](src/agents/core.py) for reference
- **No virtualenvs in containers**: Poetry configured with `virtualenvs.create false` in [Dockerfile](Dockerfile)
- **Less is more**: If you can solve it in 10 lines instead of 50, do it

### Code Examples
```python
# ✅ Good: Type hints, logging, docstring, minimal
def respond(self, conversation_history: List[Dict]) -> tuple[str, float]:
    """Generate a response based on conversation history.
    
    Args:
        conversation_history: List of messages with 'agent' and 'message' keys
        
    Returns:
        Tuple of (response message, generation time in seconds)
    """
    logger.info(f"{self.name} generating response...")
    # ... implementation

# ❌ Avoid: Over-engineering for POC
# Don't add: retry logic, caching layers, complex error recovery, etc.
# Keep it simple - if it breaks, we'll see it in logs
```

## Architecture

### Container Structure
- **app**: Streamlit UI + agent logic (Python 3.11, Poetry)
- **ollama**: LLM inference (mistral/llama3.1 models)
- **weaviate**: Multi-tenant vector database for RAG

See [docker-compose.yml](docker-compose.yml) for service definitions and networking.

### Key Components
- **Agent classes** ([src/agents/core.py](src/agents/core.py)): `Agent` (AI), `HumanAgent` (placeholder), `MultiAgentOrchestrator` (conversation manager)
- **UI layer** ([src/app.py](src/app.py)): Streamlit interface with session state management
- **RAG pipeline**: LlamaIndex + Weaviate (multi-tenancy per company)

### Data Flow
1. User creates scenario → LLM suggests agents
2. Orchestrator runs round-robin conversation
3. Each agent calls Ollama `/api/chat` endpoint
4. Responses logged to session state + optionally Weaviate
5. UI updates in real-time via streaming

## Configuration

### Environment Variables
All configuration via env vars - **never hardcode URLs or models**:
- `OLLAMA_URL`: Default `http://ollama:11434`
- `WEAVIATE_URL`: Default `http://weaviate:8080`
- `DEFAULT_MODEL`: LLM model name (e.g., `mistral`, `llama3.1`)
- `MAX_TURNS`: Conversation limit (default `30`)

See pattern in [src/agents/core.py](src/agents/core.py):
```python
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
```

## Build and Test

### Development Workflow
```bash
# Start all services (detached)
docker-compose up -d

# View logs
make logs-app        # App logs only
make logs            # All services

# Restart after code changes (volumes auto-sync)
make restart

# Full rebuild
make build

# Stop and clean
make down            # Stop containers
make clean           # Remove volumes too
```

### Testing
```bash
# Run test scripts inside container
docker-compose exec app python scripts/test_agents.py

# Initialize Weaviate (first run only)
docker-compose exec app python scripts/init_weaviate.py
```

### First-Time Setup
```bash
# 1. Start services
docker-compose up -d

# 2. Download models (5GB, 5-10 minutes)
docker-compose exec ollama ollama pull mistral
docker-compose exec ollama ollama pull nomic-embed-text

# 3. Initialize database
docker-compose exec app python scripts/init_weaviate.py

# 4. Access UI
open http://localhost:8501
```

## Project Conventions

### Agent Response Pattern
Agents **always return `(message: str, generation_time: float)` tuple**. See [src/agents/core.py:60-130](src/agents/core.py#L60-L130).

### Error Handling
- **Keep it simple**: Log error, raise exception with clear message
- **Timeouts**: 300s for Ollama calls (CPU-only execution)
- **Let it fail fast**: Don't over-engineer error recovery for POC
- **Trust the logs**: If something breaks, logs will tell you why

Example from [src/agents/core.py:100-127](src/agents/core.py#L100-L127):
```python
try:
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
except requests.exceptions.Timeout:
    logger.error(f"{self.name}: Request timed out")
    raise RuntimeError(f"Agent {self.name} timed out")
```

### Conversation Termination
Simple keyword detection in orchestrator (`_should_terminate()`) - looks for "deal", "agreed", "contract", etc. in last message.

### Streaming vs Batch
- `run()`: Returns full conversation history
- `run_streaming()`: Generator yielding messages for real-time UI updates

Both methods in [MultiAgentOrchestrator](src/agents/core.py).

## Integration Points

### Ollama API
- **Endpoint**: `/api/chat` (non-streaming) or streaming variant
- **Method**: POST with messages array
- **Payload**: 
  ```json
  {
    "model": "mistral",
    "messages": [{"role": "system", "content": "..."}, ...],
    "stream": false,
    "options": {"temperature": 0.7, "num_predict": 200}
  }
  ```
- **Response**: `{"message": {"content": "..."}}`

See [src/agents/core.py:84-98](src/agents/core.py#L84-L98) for implementation.

### Weaviate
- **Multi-tenancy**: Collections use tenant per company (e.g., `hpe`, `toyota`)
- **Collections**: `Document` (RAG chunks), `ConversationHistory` (logs)
- **Initialization**: Run [scripts/init_weaviate.py](scripts/init_weaviate.py) to create schemas

## Common Tasks

### Add New Agent Type
1. Subclass `Agent` in [src/agents/core.py](src/agents/core.py)
2. Override `respond()` method
3. Update orchestrator if special handling needed

### Change LLM Model
```bash
# Download new model
docker-compose exec ollama ollama pull llama3.1

# Update environment variable in docker-compose.yml
DEFAULT_MODEL: llama3.1

# Restart
make restart
```

### Debug LLM Responses
Check logs for JSON payloads and responses:
```bash
make logs-app | grep "generating response"
```

### Add Document to RAG
```bash
# Copy document to data/documents/<company>/
cp file.pdf data/documents/toyota/

# Ingest (script TBD - RAG implementation in progress)
docker-compose exec app python scripts/ingest_documents.py \
  --company toyota --path /app/data/documents/toyota/
```

## POC Philosophy
- **Incomplete is OK**: Not all features are implemented - that's intentional
- **Iterate quickly**: Add functionality as needed, not preemptively
- **Simple wins**: 10 clear lines > 50 robust lines
- **Local dev only**: No cloud, no auth, no production concerns
- **Fail loudly**: Clear errors in logs are better than silent failures
