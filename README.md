# Callisto - Multi-Agent Conversation Simulator

A local, Dockerized platform for building and testing AI agent-based PoCs with multi-agent conversation simulations.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## What is Callisto?

Callisto is a **standardized AI agent platform** designed for rapid PoC development. It enables you to:

- 🤖 **Simulate multi-agent B2B conversations** (e.g., HPE sales vs Toyota procurement)
- 🧙 **Generate scenarios dynamically** using LLM-powered wizards
- 👤 **Participate in conversations** or watch agents interact autonomously
- 📊 **Track sentiment in real-time** and analyze outcomes
- 🔒 **Run 100% locally** with no cloud dependencies

**Perfect for:** AI/ML engineers building PoCs, testing conversation strategies, or experimenting with different LLM approaches.

---

## Quick Start

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **16GB RAM** (recommended)
- **50GB free disk space**

### Setup (15 minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd callisto

# 2. Start services
docker-compose -f docker-compose.dev.yml up -d

# 3. Wait for services to be ready (~30-60 seconds)
docker-compose ps

# 4. Download LLM models (first time only, ~5GB)
docker-compose exec ollama ollama pull llama3.1
docker-compose exec ollama ollama pull nomic-embed-text

# 5. Initialize Weaviate
docker-compose exec app python scripts/init_weaviate.py

# 6. Load sample data
docker-compose exec app python scripts/ingest_documents.py \
  --company HPE --path /app/data/documents/hpe/

docker-compose exec app python scripts/ingest_documents.py \
  --company Toyota --path /app/data/documents/toyota/

# 7. Access the UI
open http://localhost:8501
```

**That's it!** You're ready to create your first agent scenario.

---

## Your First Simulation

### Scenario: HPE Selling Servers to Toyota

1. **Open UI:** http://localhost:8501

2. **Create Scenario:**
   - Select client: **Toyota**
   - Describe scenario: `"Negotiate server purchase contract"`
   - Click **Generate Agents**

3. **Review Suggested Agents:**
   - Agent 1: Sarah (HPE - Sales Engineer)
   - Agent 2: Yuki (Toyota - IT Procurement Manager)

4. **Run Simulation:**
   - Click **Run Simulation**
   - Watch agents negotiate in real-time
   - See sentiment chart update

5. **Review Results:**
   - Total turns taken
   - Final sentiment scores
   - Conversation outcome

**Pro Tip:** Check "I want to participate" to act as the HPE sales agent yourself!

---

## Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **Dynamic Scenario Creation** | Describe your scenario in natural language → LLM generates appropriate agents |
| **Multi-Tenant Knowledge** | Each company has isolated document storage with RAG retrieval |
| **Autonomous Conversations** | Watch agents negotiate without human intervention |
| **Human-in-the-Loop** | Participate as one of the agents in real-time |
| **Real-Time Sentiment** | Track emotional tone throughout conversation |
| **Full Reproducibility** | All configurations and prompts saved for analysis |

### 🛠️ Tech Stack

- **LLM Server:** Ollama (llama3.1)
- **Vector Database:** Weaviate (multi-tenant)
- **RAG Pipeline:** LlamaIndex
- **UI:** Streamlit
- **Orchestration:** Docker Compose
- **Language:** Python 3.11
- **Dependencies:** Poetry

---

## Architecture

**3-Container System:**
- **app**: Streamlit UI + agent logic (Python 3.11)
- **ollama**: LLM inference (llama3.1/mistral)
- **weaviate**: Multi-tenant vector database

**Data Flow:** User creates scenario → LLM generates agents → Agents use RAG (Weaviate) → Ollama generates responses → Real-time UI updates

📖 For detailed architecture diagrams and integration points, see [.github/copilot-instructions.md](.github/copilot-instructions.md#architecture)

---

## Use Cases

### 1. Practice Client Conversations
Prepare for real client meetings by simulating tough negotiations.

**Example:** Practice responding to a client demanding 30% discount.

### 2. Compare LLM Performance
Test which model performs best for your use case.

**Example:** Run same scenario with llama3.1 vs mistral, compare outcomes.

### 3. Test Conversation Strategies
Validate different approaches before implementing.

**Example:** Aggressive pricing vs relationship-focused approach.

### 4. Multi-Party Simulations
Simulate complex deals with 4+ stakeholders.

**Example:** HPE sales + tech vs Client procurement + legal counsel.

---

## Project Structure

```
callisto/
├── docker-compose.dev.yml      # Docker services definition
├── Dockerfile                  # App container build
├── pyproject.toml              # Python dependencies (Poetry)
├── README.md                   # This file
│
├── src/                        # Application code
│   ├── app.py                  # Streamlit UI
│   ├── agents/                 # Agent logic
│   ├── rag/                    # LlamaIndex RAG
│   └── utils/                  # Utilities
│
├── scripts/                    # Setup & maintenance
│   ├── init_weaviate.py       # Initialize database
│   └── ingest_documents.py    # Load documents
│
└── data/                       # Persistent data
    ├── conversations/          # Saved conversations (JSON)
    └── documents/              # Input documents (PDF, DOCX)
        ├── hpe/
        ├── toyota/
        └── microsoft/
```

---

## Adding Your Own Data

### 1. Add Documents

Place documents in `data/documents/<company_name>/`:

```bash
mkdir -p data/documents/acme
cp ~/contracts/*.pdf data/documents/acme/
```

### 2. Ingest Documents

```bash
docker-compose exec app python scripts/ingest_documents.py \
  --company "Acme Corp" \
  --path /app/data/documents/acme/
```

The script will:
- Convert company name to tenant ID (`acme_corp`)
- Extract text from PDFs/DOCX
- Chunk content into 512-token segments
- Generate embeddings via Ollama
- Store in Weaviate with tenant isolation

### 3. Use in Scenarios

Select "Acme Corp" in the client dropdown, and agents will have access to those documents.

---

## Advanced Usage

### Human Participation Mode

Act as one of the agents yourself:

1. Check **"I want to participate"** in scenario wizard
2. System generates: You + AI client agent
3. Chat with AI client in real-time
4. System tracks sentiment of client responses

### Multi-Agent Scenarios

Create complex simulations with 4+ agents:

**Example Prompt:**
```
"Enterprise deal with HPE and Microsoft involving 
technical architects and legal counsel on both sides"
```

System generates:
- HPE Account Manager
- HPE Technical Architect
- Microsoft Procurement Officer
- Microsoft Legal Counsel

### Regenerate Agents

Not satisfied with suggested agents?
1. Click **"Regenerate Agents"**
2. System creates new configuration with different roles/names
3. Repeat until satisfied

---

## Configuration

### Environment Variables

Set in `docker-compose.dev.yml`:

```yaml
environment:
  - WEAVIATE_URL=http://weaviate:8080
  - OLLAMA_URL=http://ollama:11434
  - DEFAULT_MODEL=llama3.1
  - MAX_TURNS=30
```

### Streamlit Customization

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f ollama
docker-compose logs -f weaviate

# Restart services
docker-compose restart
```

### Ollama Model Not Found

```bash
# List downloaded models
docker-compose exec ollama ollama list

# Pull missing model
docker-compose exec ollama ollama pull llama3.1
```

### Out of Memory

Increase Docker memory limit:
- **Docker Desktop:** Settings → Resources → Memory (set to 12GB+)

### Slow Responses

- Use smaller model: `ollama pull llama3.1:8b`
- Reduce context window in agent prompts
- Close other applications

### Weaviate Connection Error

```bash
# Check Weaviate health
curl http://localhost:8080/v1/.well-known/ready

# Restart Weaviate
docker-compose restart weaviate
```

---

## Development

### Hot-Reload

Code changes in `src/` automatically reload in Streamlit:

```bash
# Edit src/app.py
# Save file
# Streamlit detects change and reloads (5-10 seconds)
```

### Add Python Dependencies

```bash
# Add package
poetry add <package-name>

# Update lock file
poetry lock

# Rebuild container
docker-compose build app
docker-compose up -d app
```

### Run Tests (Future)

```bash
docker-compose exec app pytest
```

---

## Code Quality

This project uses **automated AI agents** for continuous quality improvement:

- **`@quality` agent**: Analyzes codebase and generates [ProjectScore.md](documentation/ProjectScore.md) with detailed metrics
- **`@fixer` agent**: Automatically applies improvements based on quality report
- **Target**: 85%+ quality score (currently: 92.5%)

The workflow runs iteratively (Quality → Fixer → Testing) until target is achieved. 

📊 **Metrics tracked:**
- Simplicity (file/function size)
- DRY principle (code duplication)
- SOLID principles (SRP)
- Code standards (type hints, docstrings, logging)

🔧 **Usage:** Invoke `@quality` in GitHub Copilot to trigger a quality audit and auto-fix cycle.

See [.github/copilot-instructions.md](.github/copilot-instructions.md#ai-agents-for-code-quality) for complete workflow details.

---

## Performance

### Expected Response Times (Alpha)

| Operation | Target | Actual (Laptop) |
|-----------|--------|-----------------|
| Scenario generation | < 10s | ~8s |
| Agent response (no RAG) | < 5s | ~3s |
| RAG retrieval | < 3s | ~2s |
| Page load | < 2s | ~1s |

**Hardware:** MacBook Pro M2, 16GB RAM

### Resource Usage

- **Idle:** ~2GB RAM
- **Active conversation:** ~6GB RAM
- **Disk:** ~15GB (models + data)

---

## Roadmap

**Current Status:** ~40% complete (Phases 1-2 done, RAG/persistence in progress)

📋 For detailed roadmap, timelines, and task checklists, see [Implementation Plan](documentation/Implementation%20Plan%20-%20Callisto.md)

---

## FAQ

**Q: Does this work offline?**  
A: Yes! All processing is local. No internet required after initial setup.

**Q: Can I use different LLMs?**  
A: Yes. Pull any Ollama-supported model (`ollama pull mistral`) and update config.

**Q: How accurate is sentiment analysis?**  
A: Uses distilBERT (~80% accuracy). Good for trends, not perfect.

**Q: Can agents access the internet?**  
A: No. Agents only access uploaded documents via RAG.

**Q: How do I delete old conversations?**  
A: Delete from `data/conversations/` folder. Weaviate cleanup coming in Phase 2.

**Q: Can I run this in production?**  
A: Not recommended. Alpha is for experimentation. See Phase 5 for production hardening.

---

## Documentation

Comprehensive documentation in `docs/`:

- **[Business Requirements](docs/Business%20Requirements%20Document%20-%20Callisto.md)** - Why this exists, use cases, goals
- **[Technical Requirements](docs/Technical%20Requirements%20Document%20-%20Callisto.md)** - Architecture, APIs, data models
- **[Implementation Plan](docs/Implementation%20Plan%20-%20Callisto.md)** - Development roadmap, phases, timelines

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with:
- [Ollama](https://ollama.ai/) - Local LLM inference
- [Weaviate](https://weaviate.io/) - Vector database
- [LlamaIndex](https://www.llamaindex.ai/) - RAG framework
- [Streamlit](https://streamlit.io/) - Web UI
- [HuggingFace Transformers](https://huggingface.co/transformers/) - Sentiment analysis

---

## Contact

**Author:** Senior AI/ML Engineer  
**Project:** Callisto  
**Purpose:** Standardized local AI agent platform for PoC development

For questions or feedback, open an issue in the repository.

---

## Version History

- **v0.1.0 (Alpha)** - January 30, 2026
  - Initial release
  - Core agent functionality
  - LLM-powered scenario generation
  - Multi-tenant RAG
  - Human-in-the-loop mode
  - Real-time sentiment tracking

---

**Happy Simulating! 🤖**
