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

# Validate code refactoring
docker exec callisto-app python scripts/validate_refactoring.py

# Initialize Weaviate (first run only)
docker-compose exec app python scripts/init_weaviate.py
```

### First-Time Setup
See [README.md](../README.md#quick-start) for complete setup instructions with model downloads and initialization

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

## Critical Workflow Artifacts

**DO NOT DELETE** - These files are essential to the development workflow:

- **documentation/ProjectScore.md** - Data contract between Quality and Fixer agents. Generated by Quality, consumed by Fixer. Tracks quality metrics and improvement history across runs.
- **documentation/Implementation Plan - Callisto.md** - Active roadmap and task backlog
- **documentation/Business Requirements Document - Callisto.md** - Project charter, problem statement, success criteria
- **docker-compose.yml** - Service definitions and container orchestration
- **pyproject.toml** - Python dependencies managed by Poetry
- **.github/copilot-instructions.md** - AI agent context and guidelines (this file)

## AI Agents for Code Quality

### Quality Agent
**Purpose**: Measure and improve POC code quality iteratively until 85%+ score is achieved.

**Workflow**:
1. Analyze Python codebase (src/, scripts/)
2. Evaluate:
   - Type hints coverage and docstrings
   - Error handling, logging patterns
   - Code complexity and file size
   - **Cross-file consolidation opportunities**: Duplicate logic, similar patterns, scattered utilities
   - **Within-file simplification**: Unnecessary complexity, over-engineering
   - Adherence to project guidelines
3. Provide detailed quality score with breakdown
4. **Automatically invoke Fixer agent** to apply improvements
5. After Fixer completes, **automatically invoke Testing agent** to validate changes
6. Repeat until 85%+ score achieved

**Evaluation Criteria**:
- **DRY violations**: Look for duplicate code both within files AND across multiple files
- **Consolidation opportunities**: Identify scattered logic that could be unified into shared utilities
- **Simplification potential**: Find over-engineered solutions that could be simpler

**Output**: Quality report saved to **[documentation/ProjectScore.md](documentation/ProjectScore.md)**
  - **CRITICAL ARTIFACT**: This file is the data contract between Quality and Fixer agents - never delete
  - Contains "Issues to Fix" section that Fixer agent reads as input
  - Tracks quality score history and improvements across multiple runs
  - Generated output becomes Fixer's authoritative task list

### Fixer Agent
**Purpose**: Fix code quality issues identified by Quality agent while respecting POC philosophy.

**Workflow**:
1. Receive issues from Quality agent report
2. **CRITICAL - Consolidation First**: Before any other fixes:
   - Scan for duplicate code patterns across ALL files
   - Identify scattered utilities that serve the same purpose
   - Consolidate cross-file duplicates into shared modules (e.g., src/utils/)
   - Merge similar functions/classes that exist in multiple places
3. **CRITICAL - Simplify 3 Times**: Before splitting files, attempt to simplify code **3 times**:
   - Attempt 1: Remove unnecessary complexity, consolidate logic, extract small helpers
   - Attempt 2: Apply DRY principle, merge duplicate code, inline trivial functions
   - Attempt 3: Refactor for clarity, reduce nesting, simplify conditionals
4. **Only split files if**:
   - All consolidation and simplification attempts fail to bring file under 300 lines
   - AND splitting creates files with distinct, separate concerns
   - AND splitting does NOT result in multiple files with the same concern
5. Apply fixes in priority order: **cross-file consolidation** → type hints → DRY → simplification → splitting (last resort)
6. Follow POC philosophy: simple, minimal, functional
7. **Never invoke Testing agent** - Quality agent handles the workflow

**Rules**:
- **Consolidate before splitting**: Always look for opportunities to merge/unify before creating new files
- **Cross-file awareness**: Don't fix files in isolation - consider the entire codebase
- Splitting is the LAST resort, not the first solution
- Don't split if it creates artificial boundaries
- Don't split if files share the same responsibility
- Always preserve backwards compatibility (re-exports if needed)

**Examples of Cross-File Consolidation**:
- Multiple files with similar utility functions → Consolidate to [src/utils/helpers.py](src/utils/helpers.py)
- Duplicate validation logic in different modules → Extract to shared validator
- Same configuration pattern repeated → Create config module

### Testing Agent  
**Purpose**: Validate that all code changes work correctly after Fixer completes.

**Workflow**:
1. Run all test scripts in the project:
   - `docker-compose exec app python scripts/test_agents.py`
   - Any other discovered test files
2. Verify services are healthy (Ollama, Weaviate)
3. Check for import errors or syntax issues
4. If ANY test fails or errors occur:
   - Document the failure with full error details
   - **Automatically invoke Fixer agent** with specific issues to fix
   - Fixer fixes the issues and Testing runs again
5. Repeat until all tests pass
6. Report success with summary of what was validated

**Output**: Test results summary with pass/fail status for each component
