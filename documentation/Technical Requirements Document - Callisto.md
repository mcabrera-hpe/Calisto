# Technical Requirements Document - Callisto

**Project:** Multi-Agent Conversation Simulator  
**Version:** Alpha  
**Date:** January 30, 2026  
**Author:** Senior AI/ML Engineer

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Docker Compose Environment                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Container: app (Python 3.11)                        │  │
│  │                                                       │  │
│  │  Streamlit Process                                   │  │
│  │  ├── UI Layer (src/app.py)                          │  │
│  │  ├── Agent Logic (src/agents/)                      │  │
│  │  ├── LlamaIndex RAG (src/rag/)                      │  │
│  │  └── Utilities (src/utils/)                         │  │
│  │                                                       │  │
│  │  HTTP Clients:                                       │  │
│  │  ├── → Ollama API (http://ollama:11434)            │──┼──→ ollama container
│  │  └── → Weaviate API (http://weaviate:8080)         │──┼──→ weaviate container
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Container: weaviate                                  │  │
│  │  ├── Vector Database Engine                          │  │
│  │  ├── Multi-Tenant Collections                        │  │
│  │  │   ├── Documents (tenants: hpe, toyota, ...)      │  │
│  │  │   └── ConversationHistory                         │  │
│  │  └── HTTP API (port 8080)                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Container: ollama                                    │  │
│  │  ├── LLM Inference Engine                            │  │
│  │  ├── Models: llama3.1, nomic-embed-text             │  │
│  │  └── HTTP API (port 11434)                           │  │
│  │      ├── /api/chat (streaming + non-streaming)      │  │
│  │      └── /api/embeddings                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Volumes:                                                    │
│  ├── ./src → /app/src (hot-reload)                         │
│  ├── ./data → /app/data (persistent)                       │
│  └── ollama_models → /root/.ollama (model storage)         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

#### App Container
- **Streamlit UI:** User interface, input handling, display
- **Agent Orchestrator:** Conversation flow management
- **LlamaIndex:** Document processing, RAG pipeline
- **Sentiment Analysis:** Transformers model inference
- **Persistence:** Save/load conversations

#### Weaviate Container
- **Vector Storage:** Multi-tenant document embeddings
- **Metadata Storage:** Conversation history
- **Similarity Search:** Top-K retrieval per tenant

#### Ollama Container
- **LLM Inference:** Generate agent responses
- **Embedding Generation:** Convert text to vectors
- **Model Management:** Download and cache models

---

## 2. Technology Stack

### 2.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Container Orchestration** | Docker Compose | Latest | Service management |
| **Python Runtime** | Python | 3.11 | Application runtime |
| **Dependency Management** | Poetry | 1.7+ | Package management |
| **LLM Server** | Ollama | Latest | Local LLM inference |
| **Vector Database** | Weaviate | 1.24+ | Multi-tenant vector storage |
| **RAG Framework** | LlamaIndex | 0.10+ | Document processing pipeline |
| **UI Framework** | Streamlit | 1.30+ | Web interface |
| **Sentiment Model** | Transformers | 4.36+ | Sentiment analysis |

### 2.2 Python Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"

# LlamaIndex ecosystem
llama-index-core = "^0.10"
llama-index-vector-stores-weaviate = "^0.1"
llama-index-embeddings-ollama = "^0.1"

# Core libraries
weaviate-client = "^4.0"
streamlit = "^1.30"
transformers = "^4.36"
torch = "^2.1"
requests = "^2.31"

# Document processing
pypdf = "^4.0"
python-docx = "^1.0"

# Development
pytest = "^7.4" (optional)
```

### 2.3 Models

| Model | Size | Purpose | Download |
|-------|------|---------|----------|
| **llama3.1:8b** | ~4.7GB | Agent LLM inference | `ollama pull llama3.1` |
| **nomic-embed-text** | ~270MB | Document embeddings | `ollama pull nomic-embed-text` |
| **distilbert-base-uncased-finetuned-sst-2-english** | ~255MB | Sentiment analysis | Auto-downloaded by transformers |

---

## 3. Data Architecture

### 3.1 Weaviate Schema

#### Collection: Documents (Multi-Tenant)

```python
{
    "class": "Documents",
    "multiTenancyConfig": {"enabled": True},
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Document chunk content"
        },
        {
            "name": "source",
            "dataType": ["text"],
            "description": "Original document filename"
        },
        {
            "name": "chunk_index",
            "dataType": ["int"],
            "description": "Chunk position in document"
        },
        {
            "name": "metadata",
            "dataType": ["text"],
            "description": "JSON metadata (date, author, etc.)"
        }
    ],
    "vectorizer": "none",  # We provide vectors via Ollama
}
```

**Tenants:** `hpe`, `toyota`, `microsoft`, etc. (slugified company names)

#### Collection: ConversationHistory

```python
{
    "class": "ConversationHistory",
    "properties": [
        {
            "name": "scenario_description",
            "dataType": ["text"]
        },
        {
            "name": "agent_configs",
            "dataType": ["text"],  # JSON array
            "description": "Agent names, companies, roles, system prompts, tools"
        },
        {
            "name": "messages",
            "dataType": ["text"],  # JSON array
            "description": "Full conversation with sentiment scores"
        },
        {
            "name": "metrics",
            "dataType": ["text"],  # JSON object
            "description": "Total turns, final sentiment, outcome"
        },
        {
            "name": "timestamp",
            "dataType": ["date"]
        },
        {
            "name": "client_company",
            "dataType": ["text"]
        }
    ]
}
```

### 3.2 File System Structure

```
data/
├── conversations/              # JSON exports (backup)
│   ├── 2026-01-30_hpe-toyota_001.json
│   └── 2026-01-30_hpe-microsoft_001.json
│
└── documents/                  # Input documents for ingestion
    ├── hpe/
    │   ├── product_catalog.pdf
    │   ├── pricing_guide_2026.pdf
    │   └── technical_specs_dl380.pdf
    ├── toyota/
    │   └── procurement_policy.pdf
    └── microsoft/
        └── enterprise_contract_template.docx
```

### 3.3 Conversation JSON Export Format

```json
{
  "scenario": {
    "description": "Negotiate server purchase contract",
    "client_company": "toyota",
    "timestamp": "2026-01-30T10:30:00Z"
  },
  "agents": [
    {
      "name": "Sarah",
      "company": "HPE",
      "role": "Enterprise Sales Manager",
      "objective": "Sell 100 servers, maintain 15% margin",
      "system_prompt": "You are Sarah, an Enterprise Sales Manager at HPE...",
      "tools": ["rag_hpe", "pricing"]
    },
    {
      "name": "Yuki",
      "company": "Toyota",
      "role": "IT Procurement Manager",
      "objective": "Get best price, ensure SLA",
      "system_prompt": "You are Yuki, IT Procurement Manager at Toyota...",
      "tools": ["rag_toyota"]
    }
  ],
  "conversation": [
    {
      "turn": 1,
      "agent": "Yuki",
      "company": "Toyota",
      "message": "We need 100 servers for our data center upgrade...",
      "sentiment": 0.5,
      "timestamp": "2026-01-30T10:31:15Z"
    },
    {
      "turn": 2,
      "agent": "Sarah",
      "company": "HPE",
      "message": "Our ProLiant DL380 Gen11 is perfect for your needs...",
      "sentiment": 0.7,
      "timestamp": "2026-01-30T10:31:42Z"
    }
  ],
  "metrics": {
    "total_turns": 12,
    "final_client_sentiment": 0.75,
    "final_company_sentiment": 0.65,
    "outcome_keywords": ["agreement", "contract", "signed"],
    "duration_seconds": 145
  }
}
```

---

## 4. API Specifications

### 4.1 Ollama API

#### Chat Endpoint (Agent Inference)

**Request:**
```http
POST http://ollama:11434/api/chat
Content-Type: application/json

{
  "model": "llama3.1",
  "messages": [
    {"role": "system", "content": "You are a sales agent..."},
    {"role": "user", "content": "What's your best price?"}
  ],
  "stream": true,
  "options": {
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

**Response (Streaming):**
```json
{"message": {"role": "assistant", "content": "Our"}}
{"message": {"role": "assistant", "content": " ProLiant"}}
{"message": {"role": "assistant", "content": " servers"}}
...
{"done": true}
```

#### Embeddings Endpoint

**Request:**
```http
POST http://ollama:11434/api/embeddings
Content-Type: application/json

{
  "model": "nomic-embed-text",
  "prompt": "Server specifications for data center deployment"
}
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, 0.789, ...]  // 768-dim vector
}
```

### 4.2 Weaviate API (via Python Client)

#### Tenant Management
```python
from weaviate.classes.tenants import Tenant

# Create tenant
collection.tenants.create([Tenant(name="toyota")])

# List tenants
tenants = collection.tenants.get()
```

#### Insert Documents
```python
collection.data.insert_many(
    objects=[
        {"content": "Server specs...", "source": "catalog.pdf"},
        {"content": "Pricing info...", "source": "pricing.pdf"}
    ],
    vectors=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    tenant="hpe"
)
```

#### Query with Tenant
```python
response = collection.query.near_vector(
    near_vector=[0.1, 0.2, ...],
    limit=5,
    tenant="toyota"
)
```

---

## 5. Key Algorithms & Logic

### 5.1 Scenario Suggestion (LLM-Powered)

**Few-Shot Prompt Template:**
```python
SCENARIO_PROMPT = """
You are an expert at creating multi-agent conversation scenarios.
Given a scenario description, suggest appropriate agents.

Examples:

INPUT: "HPE selling servers to Toyota"
OUTPUT:
{
  "agents": [
    {"name": "Sarah", "company": "HPE", "role": "Sales Engineer", "objective": "Sell 100 servers"},
    {"name": "Yuki", "company": "Toyota", "role": "IT Procurement", "objective": "Get best price"}
  ],
  "initial_message": "We're evaluating server options for our data center expansion."
}

INPUT: "Complex enterprise deal with Microsoft, need technical and legal review"
OUTPUT:
{
  "agents": [
    {"name": "Alex", "company": "HPE", "role": "Account Manager", "objective": "Close deal"},
    {"name": "Mike", "company": "HPE", "role": "Technical Architect", "objective": "Address tech requirements"},
    {"name": "David", "company": "Microsoft", "role": "Procurement Officer", "objective": "Negotiate terms"},
    {"name": "Emily", "company": "Microsoft", "role": "Legal Counsel", "objective": "Review contract"}
  ],
  "initial_message": "We need to finalize the enterprise agreement with proper technical and legal review."
}

Now generate agents for:
INPUT: {user_scenario}
OUTPUT:
"""
```

**Processing:**
1. User enters scenario description
2. System sends to Ollama with few-shot prompt
3. Parse JSON response
4. Validate agent structure
5. Display preview to user
6. If user rejects, regenerate with modified prompt

### 5.2 Tool Assignment (Keyword-Based)

```python
def assign_tools(role: str, objective: str) -> List[str]:
    """Simple keyword matching for tool assignment"""
    
    tools = []
    text = f"{role} {objective}".lower()
    
    # Keyword → Tool mapping
    if any(word in text for word in ["technical", "tech", "engineer", "architect"]):
        tools.append("technical_docs")
    
    if any(word in text for word in ["legal", "counsel", "contract", "compliance"]):
        tools.append("legal_docs")
    
    if any(word in text for word in ["price", "pricing", "cost", "budget"]):
        tools.append("pricing_tool")
    
    # All agents get RAG access to their company's data
    tools.append("rag")
    
    return tools
```

### 5.3 Multi-Agent Orchestrator

```python
class MultiAgentOrchestrator:
    def __init__(self, agents: List[Agent], max_turns: int = 30):
        self.agents = agents
        self.max_turns = max_turns
        self.history = []
    
    def run(self, initial_message: str) -> List[Dict]:
        """Execute conversation with round-robin agent selection"""
        
        current_message = initial_message
        agent_index = 0
        
        for turn in range(self.max_turns):
            # Get current agent
            current_agent = self.agents[agent_index]
            
            # Skip if agent doesn't want to respond
            if not current_agent.should_respond(current_message, self.history):
                agent_index = (agent_index + 1) % len(self.agents)
                continue
            
            # Generate response (human input or LLM)
            if isinstance(current_agent, HumanAgent):
                response = self.get_human_input(current_message)
            else:
                response = current_agent.respond(current_message, self.history)
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(response)
            
            # Record in history
            self.history.append({
                "turn": turn + 1,
                "agent": current_agent.name,
                "company": current_agent.company,
                "message": response,
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat()
            })
            
            # Check termination conditions
            if self.should_terminate():
                break
            
            # Next agent
            current_message = response
            agent_index = (agent_index + 1) % len(self.agents)
        
        return self.history
    
    def should_terminate(self) -> bool:
        """Check if conversation should end"""
        if len(self.history) >= self.max_turns:
            return True
        
        # Check sentiment-based termination
        if len(self.history) >= 5:
            recent_sentiment = [msg["sentiment"] for msg in self.history[-5:]]
            avg_sentiment = sum(recent_sentiment) / len(recent_sentiment)
            
            # End if very negative (deal falling apart)
            if avg_sentiment < 0.3:
                return True
            
            # End if very positive (deal likely done)
            if avg_sentiment > 0.8:
                return True
        
        # Check for outcome keywords
        last_message = self.history[-1]["message"].lower()
        if any(word in last_message for word in ["agreement", "deal", "signed", "approved"]):
            return True
        
        return False
```

### 5.4 RAG Retrieval (LlamaIndex)

```python
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding

class RAGTool:
    def __init__(self, tenant_name: str):
        self.tenant = tenant_name
        
        # Weaviate connection
        weaviate_client = weaviate.Client("http://weaviate:8080")
        
        # Vector store with tenant
        self.vector_store = WeaviateVectorStore(
            weaviate_client=weaviate_client,
            index_name="Documents",
            tenant=self.tenant
        )
        
        # Embedding model
        embed_model = OllamaEmbedding(
            model_name="nomic-embed-text",
            base_url="http://ollama:11434"
        )
        
        # Create index
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=embed_model
        )
    
    def query(self, question: str, top_k: int = 5) -> str:
        """Retrieve relevant context"""
        query_engine = self.index.as_query_engine(
            similarity_top_k=top_k,
            streaming=False
        )
        response = query_engine.query(question)
        return str(response)
```

### 5.5 Streaming LLM Response

```python
import requests
import json

def stream_llm_response(messages: List[Dict], model: str = "llama3.1"):
    """Stream response from Ollama token by token"""
    
    response = requests.post(
        "http://ollama:11434/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": True
        },
        stream=True
    )
    
    full_response = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if "message" in chunk:
                token = chunk["message"]["content"]
                full_response += token
                yield token  # Stream to UI
    
    return full_response
```

---

## 6. Infrastructure Specifications

### 6.1 Docker Compose Configuration

**File:** `docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  weaviate:
    image: semitechnologies/weaviate:1.24.1
    container_name: callisto_weaviate
    restart: unless-stopped
    environment:
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      QUERY_DEFAULTS_LIMIT: 25
      DEFAULT_VECTORIZER_MODULE: 'none'
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8080/v1/.well-known/ready"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    container_name: callisto_ollama
    restart: unless-stopped
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 30s
      timeout: 10s
      retries: 3

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: callisto_app
    restart: unless-stopped
    command: streamlit run src/app.py --server.fileWatcherType poll --server.address 0.0.0.0
    volumes:
      - ./src:/app/src              # Hot-reload
      - ./data:/app/data            # Persistent data
      - ./scripts:/app/scripts      # Scripts
      - ./.streamlit:/app/.streamlit  # Streamlit config
    ports:
      - "8501:8501"
    environment:
      - WEAVIATE_URL=http://weaviate:8080
      - OLLAMA_URL=http://ollama:11434
      - PYTHONUNBUFFERED=1
    depends_on:
      weaviate:
        condition: service_healthy
      ollama:
        condition: service_healthy

volumes:
  weaviate_data:
    driver: local
  ollama_models:
    driver: local

networks:
  default:
    name: callisto_network
```

### 6.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry (no virtualenv in container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY .streamlit/ ./.streamlit/

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command (can be overridden)
CMD ["streamlit", "run", "src/app.py", "--server.address", "0.0.0.0"]
```

### 6.3 Resource Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 20GB free
- Docker: 20.10+
- Docker Compose: 2.0+

**Recommended:**
- CPU: 8 cores
- RAM: 16GB
- Disk: 50GB free (for multiple model versions)
- GPU: Optional (speeds up inference 3-5x)

**Estimated Resource Usage:**
- Ollama container: 4-6GB RAM (with llama3.1 loaded)
- Weaviate container: 1-2GB RAM (with 100k vectors)
- App container: 1-2GB RAM (Streamlit + transformers)
- Total: ~8GB RAM actively used

---

## 7. Security Considerations

### 7.1 Alpha Security Posture

**Current State:**
- ✅ No external network exposure (localhost only)
- ✅ No authentication required (single user)
- ✅ No sensitive data storage (sample docs only)
- ❌ No input validation (trust user input)
- ❌ No rate limiting
- ❌ No audit logging

**Acceptable for Alpha because:**
- Running on local machine only
- Single developer use
- No production data
- No multi-user access

### 7.2 Future Security Requirements (Production)

If deployed beyond local development:
- Add authentication (OAuth 2.0 or JWT)
- Implement role-based access control (RBAC)
- Enable HTTPS/TLS
- Add input sanitization and validation
- Implement rate limiting
- Add audit logging
- Encrypt data at rest (Weaviate encryption)
- Add secrets management (not hardcoded)

---

## 8. Performance Requirements

### 8.1 Response Time SLAs (Alpha)

| Operation | Target | Maximum |
|-----------|--------|---------|
| Scenario generation | < 10s | 20s |
| Agent LLM response (no RAG) | < 5s | 10s |
| RAG retrieval | < 3s | 8s |
| Sentiment analysis | < 1s | 2s |
| Page load (Streamlit) | < 2s | 5s |
| Document ingestion (100 pages) | < 2min | 5min |

### 8.2 Throughput

**Alpha Target:**
- 1 concurrent conversation
- 10 agent turns/minute
- 100 documents ingested/hour

**Not Optimized For:**
- Multiple simultaneous users
- High-frequency API calls
- Real-time streaming at scale

### 8.3 Optimization Strategies (Future)

- Model quantization (4-bit, 8-bit)
- Batch embedding generation
- Weaviate query caching
- Response streaming (implemented)
- Connection pooling

---

## 9. Testing Strategy

### 9.1 Alpha Testing Scope

**Manual Testing:**
- End-to-end scenario creation and execution
- Human participation mode
- Conversation persistence and replay
- Document ingestion with different file types
- Multi-agent orchestration (2, 3, 4 agents)

**Automated Testing (Minimal):**
- Utility functions (tenant slugification)
- JSON parsing/validation
- Basic RAG retrieval

**Not Tested in Alpha:**
- Load testing
- Security testing
- Cross-browser compatibility
- Mobile responsiveness

### 9.2 Test Scenarios

1. **Happy Path:** 2-agent scenario, autonomous, successful outcome
2. **Human Mode:** User participates as company rep
3. **Multi-Agent:** 4-agent complex negotiation
4. **RAG Accuracy:** Verify correct tenant isolation
5. **Regeneration:** User rejects scenario, regenerates successfully
6. **Conversation Replay:** Load past conversation, display correctly

---

## 10. Deployment & Operations

### 10.1 Deployment Process (Alpha)

```bash
# 1. Clone repository
git clone <repo-url>
cd callisto

# 2. Start services
docker-compose -f docker-compose.dev.yml up -d

# 3. Wait for health checks (30-60 seconds)
docker-compose ps

# 4. Download models (first time only)
docker-compose exec ollama ollama pull llama3.1
docker-compose exec ollama ollama pull nomic-embed-text

# 5. Initialize Weaviate
docker-compose exec app python scripts/init_weaviate.py

# 6. Ingest sample data
docker-compose exec app python scripts/ingest_documents.py --company HPE --path /app/data/documents/hpe/
docker-compose exec app python scripts/ingest_documents.py --company Toyota --path /app/data/documents/toyota/

# 7. Access UI
open http://localhost:8501
```

### 10.2 Monitoring (Alpha)

**Container Health:**
```bash
docker-compose ps  # Check all services running
docker-compose logs -f app  # Stream application logs
```

**Disk Usage:**
```bash
docker system df  # Check Docker disk usage
```

**No Advanced Monitoring:**
- No Prometheus/Grafana
- No application metrics
- No tracing (Phoenix in future phase)

### 10.3 Backup & Recovery

**What to Backup:**
- `data/conversations/` - Exported JSON files
- `data/documents/` - Source documents (if not in version control)

**Weaviate Data:**
- Stored in Docker volume `weaviate_data`
- Can export: `docker run --rm -v weaviate_data:/weaviate -v $(pwd):/backup ...`

**Ollama Models:**
- Stored in Docker volume `ollama_models`
- Can re-download if lost (slow but safe)

### 10.4 Troubleshooting

**Common Issues:**

| Issue | Symptom | Solution |
|-------|---------|----------|
| Ollama not responding | Agent responses hang | Check `docker-compose logs ollama`, restart container |
| Weaviate connection error | RAG queries fail | Verify Weaviate health: `curl http://localhost:8080/v1/.well-known/ready` |
| Out of memory | Docker crashes | Increase Docker memory limit (Docker Desktop settings) |
| Slow responses | 20s+ per turn | Use smaller model or reduce context window |
| Model not found | Ollama error | Pull model: `docker-compose exec ollama ollama pull llama3.1` |

---

## 11. Development Guidelines

### 11.1 Code Organization

```
src/
├── app.py                 # Streamlit entry point (UI only)
├── agents/
│   ├── core.py           # Agent, HumanAgent, Orchestrator classes
│   ├── factory.py        # Dynamic agent generation
│   └── suggester.py      # LLM scenario wizard
├── rag/
│   ├── index.py          # LlamaIndex setup
│   └── retrieval.py      # RAG tools per tenant
└── utils/
    ├── persistence.py    # Save/load conversations
    └── tenants.py        # Tenant management
```

**Separation of Concerns:**
- `app.py` - UI rendering and user interaction only
- `agents/` - Business logic, no UI code
- `rag/` - Data retrieval, no business logic
- `utils/` - Pure functions, no state

### 11.2 Coding Standards

**Python Style:**
- PEP 8 compliant
- Type hints for function signatures
- Docstrings for public functions
- Max line length: 100 characters

**Example:**
```python
def generate_agent(
    name: str,
    company: str,
    role: str,
    objective: str
) -> Dict[str, Any]:
    """
    Generate complete agent configuration using LLM.
    
    Args:
        name: Agent's name
        company: Company the agent represents
        role: Agent's role/title
        objective: Agent's goal in conversation
    
    Returns:
        Dict with keys: name, company, role, system_prompt, tools
    """
    # Implementation
```

### 11.3 Error Handling

**Strategy:**
- Fail gracefully with user-friendly messages
- Log errors to console (captured by Docker logs)
- Don't crash on API failures (retry or show error in UI)

**Example:**
```python
try:
    response = requests.post(ollama_url, json=payload, timeout=30)
    response.raise_for_status()
except requests.Timeout:
    st.error("LLM request timed out. Please try again.")
    return None
except requests.ConnectionError:
    st.error("Cannot connect to Ollama. Is it running?")
    return None
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    logging.exception("LLM request failed")
    return None
```

### 11.4 Configuration Management

**Environment Variables:**
- `WEAVIATE_URL` - Weaviate endpoint (default: http://weaviate:8080)
- `OLLAMA_URL` - Ollama endpoint (default: http://ollama:11434)
- `DEFAULT_MODEL` - Default LLM model (default: llama3.1)
- `MAX_TURNS` - Max conversation turns (default: 30)

**Streamlit Secrets (Future):**
For API keys if cloud services added later

---

## 12. Acceptance Testing

### 12.1 Alpha Completion Checklist

**Infrastructure:**
- [ ] Docker Compose starts all 3 containers successfully
- [ ] All health checks pass within 60 seconds
- [ ] Ollama models download automatically or via documented command
- [ ] Weaviate initializes with correct schema

**Core Functionality:**
- [ ] User can describe scenario and get agent suggestions
- [ ] Generated agents have appropriate roles and companies
- [ ] 2-agent autonomous conversation completes successfully
- [ ] Human can participate in conversation via chat input
- [ ] Streaming responses display token-by-token in UI
- [ ] Sentiment chart updates in real-time during conversation
- [ ] RAG retrieves correct tenant-specific data
- [ ] Conversations save to Weaviate and JSON files
- [ ] Past conversations load and display correctly

**Data Management:**
- [ ] Documents ingest successfully (PDF, DOCX)
- [ ] Tenant auto-creates with warning when new company added
- [ ] Multi-tenancy enforced (agents can't access wrong tenant)
- [ ] Sample data included for HPE, Toyota, Microsoft

**Usability:**
- [ ] README enables first-time setup in 15 minutes
- [ ] UI is intuitive (no training needed)
- [ ] Error messages are clear and actionable
- [ ] Hot-reload works (code changes reflect without rebuild)

---

## 13. Future Technical Enhancements

### Phase 2: Enhanced Infrastructure
- Add Redis for caching repeated queries
- Implement connection pooling for Weaviate
- Add Nginx reverse proxy
- Implement graceful shutdown

### Phase 3: Advanced Features
- WebSocket for real-time updates (replace polling)
- GraphQL API for external integrations
- Pub/sub for multi-container scaling
- Add PostgreSQL for relational metadata

### Phase 4: Production Hardening
- Kubernetes deployment manifests
- Helm charts
- CI/CD pipeline (GitHub Actions)
- Automated testing suite
- Performance benchmarking

---

## 14. Appendix

### 14.1 Ollama API Reference
Full docs: https://github.com/ollama/ollama/blob/main/docs/api.md

### 14.2 Weaviate Python Client
Full docs: https://weaviate.io/developers/weaviate/client-libraries/python

### 14.3 LlamaIndex Documentation
Full docs: https://docs.llamaindex.ai/

### 14.4 Streamlit API Reference
Full docs: https://docs.streamlit.io/
