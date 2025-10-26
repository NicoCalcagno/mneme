<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1 align="center">🧠 Mneme</h1>

  <p align="center">
    Transform your Obsidian vault into a queryable AI-powered knowledge base
    <br />
    <em>From Greek μνήμη (mnēmē) - "memory, remembrance"</em>
    <br />
    <br />
    <a href="https://github.com/NicoCalcagno/mneme"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/NicoCalcagno/mneme/issues/new?labels=bug&template=bug-report.md">Report Bug</a>
    ·
    <a href="https://github.com/NicoCalcagno/mneme/issues/new?labels=enhancement&template=feature-request.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#features">Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#api-endpoints">API Endpoints</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#troubleshooting">Troubleshooting</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Mneme is a production-ready RAG (Retrieval-Augmented Generation) system that transforms your Obsidian vault into an intelligent, queryable knowledge base. Built on the Datapizza AI framework, it provides semantic search and conversational interfaces to interact naturally with your personal knowledge.

**Why Mneme?**
* Your notes contain valuable knowledge that's hard to recall and connect
* Traditional search only finds exact matches, missing semantic relationships
* You should be able to have natural conversations with your accumulated knowledge
* Your personal knowledge base deserves the same AI capabilities as enterprise systems

Mneme indexes your Obsidian notes with semantic embeddings, stores them in a vector database, and lets you query them using natural language through a clean chat interface.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Datapizza AI][Datapizza-badge]][Datapizza-url]
* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![Python][Python-badge]][Python-url]
* [![Docker][Docker-badge]][Docker-url]
* [![Gradio][Gradio-badge]][Gradio-url]
* [![OpenAI][OpenAI-badge]][OpenAI-url]

**Core Technologies:**
* **[Datapizza AI](https://github.com/datapizza-labs/datapizza-ai)** - RAG framework and agent orchestration
* **Qdrant Cloud** - Vector database for semantic search
* **OpenAI/Anthropic** - LLM providers for embeddings and generation
* **Loguru** - Structured logging

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Features

- 🗂️ **Automatic Ingestion** - Sync your Obsidian notes with semantic embeddings
- 🔍 **Semantic Search** - Meaning-based retrieval with Qdrant vector store
- 💬 **Chat Interface** - Clean Gradio frontend to converse with your notes
- 🧩 **Obsidian-Aware** - Full support for frontmatter, tags, and metadata
- 🔄 **Multi-LLM Support** - Works with OpenAI and Anthropic models
- 🚀 **Production Ready** - Built on enterprise-grade Datapizza AI framework
- 🐳 **Docker Ready** - Complete setup with docker-compose
- 📊 **Health Monitoring** - Built-in health checks and status endpoints
- 🎯 **Configurable RAG** - Fine-tune chunking, retrieval, and generation parameters

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Get Mneme up and running in less than 5 minutes with Docker.

### Prerequisites

Before you begin, ensure you have:

* **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
* **An Obsidian vault** with markdown notes
* **API Keys** for your LLM provider:
  - OpenAI API key ([Get one here](https://platform.openai.com/api-keys)), or
  - Anthropic API key ([Get one here](https://console.anthropic.com/))
* **Qdrant Cloud account** - [Free tier available](https://cloud.qdrant.io/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NicoCalcagno/mneme.git
   cd mneme
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your API keys and vault path
   ```

3. **Required environment variables**
   ```env
   OBSIDIAN_VAULT_PATH=/path/to/your/vault
   OPENAI_API_KEY=your-openai-key
   QDRANT_URL=https://your-cluster.cloud.qdrant.io
   QDRANT_API_KEY=your-qdrant-key
   ```

4. **Start the services**
   ```bash
   docker compose up -d
   ```

5. **Verify the API is running**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

6. **Ingest your notes**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest
   ```

7. **Open the chat interface**
   ```bash
   open http://localhost:7860
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

### Chat Interface

The Gradio interface at `http://localhost:7860` provides:
- Natural language queries to your knowledge base
- Source citations with relevance scores
- Conversation history
- Health status monitoring

**Example queries:**
- "What have I written about AI and machine learning?"
- "Summarize my notes on productivity systems"
- "Find connections between my thoughts on creativity and flow state"

### REST API

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my key insights on productivity?",
    "include_sources": true,
    "max_sources": 5
  }'
```

#### Ingestion
```bash
# Ingest all notes
curl -X POST http://localhost:8000/api/v1/ingest

# Check ingestion status
curl http://localhost:8000/api/v1/ingest/status
```

### Interactive API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONFIGURATION -->
## Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Obsidian Vault
OBSIDIAN_VAULT_PATH=/path/to/your/vault
OBSIDIAN_FILE_EXTENSIONS=.md,.markdown
OBSIDIAN_EXCLUDE_FOLDERS=.obsidian,.trash,templates

# LLM Provider
LLM_PROVIDER=openai                    # openai or anthropic
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
OPENAI_API_KEY=your-key-here

# Embeddings
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
EMBEDDING_BATCH_SIZE=10

# Vector Store (Qdrant Cloud)
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-key
VECTOR_STORE_COLLECTION=mneme_knowledge

# Chunking Strategy
CHUNKING_STRATEGY=fixed                # Recommended: fixed
CHUNK_SIZE=800                         # Recommended: 800 chars
CHUNK_OVERLAP=200

# Retrieval
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.4               # Lower if getting few results

# RAG
ENABLE_CITATIONS=true
MAX_CONVERSATION_HISTORY=10
```

### Docker Commands

```bash
# Start all services (API + Frontend)
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild after code changes
docker compose down
docker compose build
docker compose up -d

# Start API only (no frontend)
docker compose up -d mneme-api
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- API ENDPOINTS -->
## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check with vector store status |
| `/api/v1/chat` | POST | Chat with your knowledge base |
| `/api/v1/ingest` | POST | Trigger note ingestion |
| `/api/v1/ingest/status` | GET | Check ingestion status |
| `/docs` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEVELOPMENT -->
## Development

### Local Development (without Docker)

1. **Install uv** (fast Python package installer)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Setup environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

3. **Run the API**
   ```bash
   python -m api.main
   ```

4. **Run the frontend** (in another terminal)
   ```bash
   python -m gradio_chat
   ```

5. **Run ingestion**
   ```bash
   python -m ingestion.ingest
   ```

### Project Structure

```
mneme/
├── api/                    # FastAPI REST API
│   ├── main.py            # Entry point with lifespan
│   ├── dependencies.py    # Dependency injection
│   ├── middleware.py      # Request logging
│   ├── routes/            # API endpoints
│   │   ├── chat.py
│   │   ├── health.py
│   │   └── ingestion.py
│   └── models/            # Pydantic schemas
├── config/
│   └── settings.py        # Configuration from .env
├── ingestion/             # Ingestion pipeline
│   ├── parser.py          # Obsidian markdown parser
│   ├── chunker.py         # Text chunking strategies
│   ├── embedder.py        # Embedding generation
│   ├── vectorstore.py     # Qdrant operations
│   └── ingest.py          # Pipeline orchestration
├── rag/                   # RAG implementation
│   ├── agent.py           # Datapizza AI agent
│   ├── retriever.py       # Semantic retrieval
│   └── prompts.py         # System prompts
├── utils/
│   └── logging.py         # Loguru configuration
├── gradio_chat.py         # Gradio frontend
├── docker-compose.yaml    # Docker orchestration
└── Dockerfile             # Multi-stage build
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- TROUBLESHOOTING -->
## Troubleshooting

### No Search Results

**Problem:** Queries return no results or very few results.

**Solution:** Lower the `RETRIEVAL_MIN_SCORE` in your `.env` file:
```env
RETRIEVAL_MIN_SCORE=0.3  # Try 0.3 or 0.4
```

### Ingestion Fails

**Problem:** Ingestion endpoint returns errors.

**Solutions:**
- Verify `OBSIDIAN_VAULT_PATH` is correct
- In Docker, use the mounted path: `/vault/VaultName`
- Check `CHUNK_SIZE` isn't too large (recommended: 800)
- Review logs: `docker compose logs mneme-api`

### Docker Won't Start

**Problem:** Services fail to start or show old code.

**Solution:** Complete rebuild:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Port Already in Use

**Problem:** Port 8000 or 7860 is already in use.

**Solution:**
```bash
# Find and kill the process (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# Or change the port in docker-compose.yaml
```

### Environment Variables Not Loading

**Problem:** Changes to `.env` not taking effect.

**Solution:**
- Never use `docker restart` - it doesn't reload env vars
- Always: `docker compose down && docker compose up -d`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Core RAG implementation with Datapizza AI
- [x] Obsidian markdown parsing with frontmatter
- [x] Vector store integration (Qdrant)
- [x] REST API with FastAPI
- [x] Chat interface with Gradio
- [x] Docker deployment
- [ ] Incremental ingestion (only new/modified notes)
- [ ] Multi-vault support
- [ ] Advanced filtering by tags/folders
- [ ] Export conversation history
- [ ] Mobile-friendly frontend
- [ ] Obsidian plugin for inline querying

See the [open issues](https://github.com/NicoCalcagno/mneme/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Nico Calcagno - [@NicoCalcagno](https://github.com/NicoCalcagno)

Project Link: [https://github.com/NicoCalcagno/mneme](https://github.com/NicoCalcagno/mneme)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Datapizza AI](https://github.com/datapizza-labs/datapizza-ai) - For the excellent RAG framework 🍕
* [Qdrant](https://qdrant.tech) - For the powerful vector database
* [Obsidian](https://obsidian.md) - For inspiring the project
* [FastAPI](https://fastapi.tiangolo.com) - For the amazing web framework
* [Gradio](https://gradio.app) - For the beautiful UI framework
* Named after **Mneme** (Μνήμη), the Greek goddess of memory and one of the original three Muses

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<div align="center">
  <p>Made with 🧠 and ☕</p>
  <p><em>"The palest ink is better than the best memory"</em> - Chinese Proverb</p>
</div>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/NicoCalcagno/mneme.svg?style=for-the-badge
[contributors-url]: https://github.com/NicoCalcagno/mneme/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/NicoCalcagno/mneme.svg?style=for-the-badge
[forks-url]: https://github.com/NicoCalcagno/mneme/network/members
[stars-shield]: https://img.shields.io/github/stars/NicoCalcagno/mneme.svg?style=for-the-badge
[stars-url]: https://github.com/NicoCalcagno/mneme/stargazers
[issues-shield]: https://img.shields.io/github/issues/NicoCalcagno/mneme.svg?style=for-the-badge
[issues-url]: https://github.com/NicoCalcagno/mneme/issues
[license-shield]: https://img.shields.io/github/license/NicoCalcagno/mneme.svg?style=for-the-badge
[license-url]: https://github.com/NicoCalcagno/mneme/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/nico-calcagno

[Datapizza-badge]: https://img.shields.io/badge/Datapizza_AI-FF6B35?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=&logoColor=white
[Datapizza-url]: https://github.com/datapizza-labs/datapizza-ai
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://docker.com
[Gradio-badge]: https://img.shields.io/badge/Gradio-FF7C00?style=for-the-badge&logo=gradio&logoColor=white
[Gradio-url]: https://gradio.app
[OpenAI-badge]: https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white
[OpenAI-url]: https://openai.com
