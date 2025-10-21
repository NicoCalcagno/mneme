# 🧠 Mneme

> *Dal greco μνήμη (mnēmē) - "memoria, ricordo"*

Mneme trasforma il tuo vault Obsidian in un cervello digitale interrogabile. Attraverso RAG (Retrieval-Augmented Generation), indicizza tutte le tue note in un vector store e ti permette di conversare naturalmente con la tua conoscenza personale.

Non più ricerca manuale tra centinaia di note: Mneme comprende il contesto, trova connessioni semantiche e recupera istantaneamente le informazioni rilevanti per rispondere alle tue domande.

---

## ✨ Features

- 🗂️ **Ingestion automatica** - Sincronizza automaticamente le tue note da Obsidian
- 🔍 **Semantic Search** - Ricerca basata sul significato, non solo su keyword
- 💬 **Conversational Interface** - Chatta con le tue note in linguaggio naturale
- 🧩 **Obsidian-aware** - Supporto per wikilinks, backlinks, tags e metadata
- 🔄 **Multi-LLM Support** - Passa da OpenAI ad Anthropic, Mistral o altri provider
- 📊 **Built-in Observability** - Monitoraggio performance con OpenTelemetry
- 🚀 **Production Ready** - Basato su Datapizza AI, framework italiano enterprise-grade
- 🔒 **Privacy First** - Possibilità di eseguire tutto in locale

---

## 🏗️ Architettura
```
┌─────────────────────────────────────────────────────────┐
│                    Obsidian Vault                        │
│                  (markdown files)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Ingestion Pipeline  │
          │  - ObsidianParser    │
          │  - TextSplitter      │
          │  - Embeddings        │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   Vector Store       │
          │   (Qdrant/Chroma)    │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   RAG Agent          │
          │   (Datapizza AI)     │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │    FastAPI           │
          │    REST API          │
          └──────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisiti

- **Docker** (metodo consigliato) oppure
- **Python >= 3.10, < 3.13** + [uv](https://github.com/astral-sh/uv)
- Un vault Obsidian esistente
- API Key di un provider LLM (OpenAI, Anthropic, etc.)

---

### 🐳 Metodo 1: Docker (Consigliato)

Il metodo più semplice per avviare Mneme è utilizzare Docker.

#### Setup rapido

```bash
# 1. Clona il repository
git clone https://github.com/tuousername/mneme.git
cd mneme

# 2. Configura le variabili d'ambiente
cp .env.example .env
nano .env  # Modifica con i tuoi parametri

# 3. Avvia con Docker
docker-compose up -d

# 4. Verifica che sia attivo
curl http://localhost:8000/api/v1/health
```

#### Comandi Docker utili

```bash
# Avvia il server
docker-compose up -d

# Visualizza i log
docker-compose logs -f

# Ferma il server
docker-compose down

# Rebuild dopo modifiche
docker-compose up -d --build

# Avvia con osservabilità (include Zipkin)
docker-compose --profile observability up -d
```

#### Oppure con Docker diretto (senza compose)

```bash
# Build dell'immagine
docker build -t mneme:latest .

# Avvio del container
docker run -d \
  --name mneme \
  -p 8000:8000 \
  --env-file .env \
  mneme:latest

# Visualizza i log
docker logs -f mneme

# Ferma il container
docker stop mneme && docker rm mneme
```

---

### 🐍 Metodo 2: Installazione locale con Python

Per sviluppo o se preferisci non usare Docker.

#### Installazione

```bash
# 1. Installa uv (se non già installato)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clona il repository
git clone https://github.com/tuousername/mneme.git
cd mneme

# 3. Crea virtual environment e installa dipendenze
uv venv
source .venv/bin/activate  # Su Windows: .venv\Scripts\activate

# 4. Installa il progetto
uv pip install -e .

# Per sviluppo (include pytest, black, ruff, mypy)
uv pip install -e ".[dev]"

# Per embeddings locali (include sentence-transformers)
uv pip install -e ".[local]"

# Per installare tutto
uv pip install -e ".[all]"
```

#### Configurazione

```bash
# Copia il file di esempio
cp .env.example .env

# Modifica .env con i tuoi parametri
nano .env
```

#### Avvio del server

```bash
# Metodo 1: Usando il comando installato
mneme-serve

# Metodo 2: Usando Python direttamente
python -m api.main

# Con auto-reload per development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

### ⚙️ Configurazione `.env`

Copia `.env.example` in `.env` e modifica i seguenti parametri:

```env
# =========================================================================
# OBSIDIAN VAULT
# =========================================================================
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
OBSIDIAN_FILE_EXTENSIONS=.md,.markdown
OBSIDIAN_EXCLUDE_FOLDERS=.obsidian,.trash,templates

# =========================================================================
# LLM PROVIDER
# =========================================================================
LLM_PROVIDER=openai                    # openai, anthropic, google, mistral
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# =========================================================================
# API KEYS
# =========================================================================
OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-key  # Se usi Anthropic

# =========================================================================
# EMBEDDINGS
# =========================================================================
EMBEDDING_PROVIDER=openai              # openai o local
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
EMBEDDING_BATCH_SIZE=100

# =========================================================================
# VECTOR STORE
# =========================================================================
VECTOR_STORE_TYPE=qdrant               # qdrant o chroma
VECTOR_STORE_COLLECTION=mneme_knowledge

# Qdrant Cloud (production)
QDRANT_URL=https://your-cluster.region.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Qdrant Locale (development)
# QDRANT_PATH=./data/qdrant
# Commenta QDRANT_URL e QDRANT_API_KEY se usi locale

# =========================================================================
# CHUNKING
# =========================================================================
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHUNKING_STRATEGY=recursive            # recursive, fixed, semantic

# =========================================================================
# RETRIEVAL
# =========================================================================
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.7

# =========================================================================
# API SERVER
# =========================================================================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true                        # Auto-reload in development
API_WORKERS=1
CORS_ORIGINS=*
API_PREFIX=/api/v1
ENABLE_DOCS=true

# =========================================================================
# OBSERVABILITY
# =========================================================================
ENABLE_TRACING=false
LOG_LEVEL=INFO
LOG_FILE=./data/logs/mneme.log

# =========================================================================
# DEVELOPMENT
# =========================================================================
ENVIRONMENT=development                # development, production, testing
DEBUG=false
```

---

### 🧪 Verifica l'installazione

```bash
# 1. Controlla la health dell'API
curl http://localhost:8000/api/v1/health

# 2. Visualizza la documentazione interattiva
open http://localhost:8000/docs

# 3. Testa gli endpoint
curl http://localhost:8000/api/v1/ready
curl http://localhost:8000/api/v1/live
```

**Risposta health check di successo:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "timestamp": "2025-10-21T20:30:00Z",
  "vector_store_connected": true,
  "llm_provider": "openai",
  "checks": {
    "vector_store": true
  }
}
```
---

## 📁 Struttura del Progetto

```
mneme/
├── README.md
├── CLAUDE.md                     # Guida per Claude Code
├── pyproject.toml                # Configurazione progetto e dipendenze
├── docker-compose.yaml           # Docker Compose setup
├── Dockerfile                    # Docker image build
├── .env.example                  # Template configurazione
├── .gitignore
│
├── __init__.py                   # Root package init
│
├── api/                          # 🌐 REST API (FastAPI)
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── dependencies.py           # Dependency injection
│   ├── middleware.py             # Custom middleware (logging, etc)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py               # Chat endpoints
│   │   ├── health.py             # Health check endpoints
│   │   └── ingestion.py          # Ingestion trigger endpoints
│   └── models/
│       ├── __init__.py
│       ├── enums.py              # Enumerations
│       ├── common.py             # Shared models
│       ├── chat.py               # Chat request/response models
│       ├── health.py             # Health check models
│       └── ingestion.py          # Ingestion models
│
├── config/                       # ⚙️  Configurazione
│   ├── __init__.py
│   └── settings.py               # Pydantic Settings (env vars)
│
├── ingestion/                    # 📥 Pipeline di ingestion
│   ├── __init__.py
│   ├── parser.py                 # (TODO) ObsidianParser
│   ├── chunker.py                # (TODO) Text splitting
│   ├── embedder.py               # (TODO) Embedding generation
│   ├── vectorstore.py            # (TODO) Vector DB operations
│   └── ingest.py                 # (TODO) CLI entry point
│
├── rag/                          # 🤖 RAG Agent
│   ├── __init__.py
│   ├── agent.py                  # (TODO) Datapizza AI agent
│   ├── retriever.py              # (TODO) Custom retrieval
│   └── prompts.py                # (TODO) System prompts
│
├── utils/                        # 🛠️  Utilities
│   ├── __init__.py
│   └── logger.py                 # (TODO) Logging utilities
│
├── scripts/                      # 📜 Scripts di utilità
│   └── test-qdrant.py            # Test connessione Qdrant
│
├── tests/                        # (TODO) Test suite
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_agent.py
│   └── test_api.py
│
└── data/                         # 💾 Gitignored
    ├── qdrant/                   # Vector DB storage (locale)
    └── logs/                     # Application logs
```

**Nota sulla struttura:** I moduli marcati con `(TODO)` sono placeholder che verranno implementati nelle prossime fasi del progetto.

---

## 🔧 API Endpoints

L'API REST è disponibile su `http://localhost:8000` con documentazione interattiva su `/docs`.

### 🏥 Health Check

#### `GET /api/v1/health`
Verifica lo stato di salute dell'applicazione e delle sue dipendenze.

```bash
curl http://localhost:8000/api/v1/health
```

**Risposta:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "timestamp": "2025-10-21T20:30:00Z",
  "vector_store_connected": true,
  "llm_provider": "openai",
  "vector_store_documents": null,
  "checks": {
    "vector_store": true
  }
}
```

#### `GET /api/v1/ready`
Kubernetes-style readiness probe.

```bash
curl http://localhost:8000/api/v1/ready
```

#### `GET /api/v1/live`
Kubernetes-style liveness probe.

```bash
curl http://localhost:8000/api/v1/live
```

---

### 💬 Chat (TODO - Da implementare)

#### `POST /api/v1/chat`
Invia un messaggio al chatbot e ricevi una risposta basata sulle tue note Obsidian.

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cosa ho scritto sul machine learning?",
    "conversation_id": "optional-session-id",
    "include_sources": true,
    "temperature": 0.7,
    "max_tokens": 2000
  }'
```

**Risposta prevista:**
```json
{
  "conversation_id": "conv_abc123",
  "message": "Nelle tue note sul machine learning...",
  "sources": [
    {
      "file_path": "notes/ml/intro.md",
      "chunk_id": "chunk_001",
      "score": 0.95,
      "content": "Il machine learning è...",
      "metadata": {
        "tags": ["ml", "ai"],
        "created_at": "2024-01-15"
      }
    }
  ],
  "processing_time_ms": 1234.56,
  "metadata": {
    "model": "gpt-4o",
    "temperature": 0.7
  }
}
```

#### `GET /api/v1/chat/conversations`
Lista tutte le conversazioni salvate.

```bash
curl http://localhost:8000/api/v1/chat/conversations
```

#### `DELETE /api/v1/chat/conversations/{conversation_id}`
Elimina una conversazione specifica.

```bash
curl -X DELETE http://localhost:8000/api/v1/chat/conversations/conv_abc123
```

---

### 📥 Ingestion (TODO - Da implementare)

#### `POST /api/v1/ingest`
Avvia manualmente il processo di ingestion delle note Obsidian.

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "/path/to/vault",
    "incremental": true,
    "force": false,
    "dry_run": false
  }'
```

**Risposta:**
```json
{
  "status": "in_progress",
  "message": "Ingestion started in background",
  "files_processed": null,
  "files_skipped": null,
  "total_chunks": null,
  "processing_time_s": null
}
```

#### `GET /api/v1/ingest/status`
Ottieni lo stato corrente del processo di ingestion.

```bash
curl http://localhost:8000/api/v1/ingest/status
```

---

### 📚 Documentazione Interattiva

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

La documentazione interattiva permette di testare tutti gli endpoint direttamente dal browser.

---

## 🎯 Roadmap

### ✅ Fase 1: Foundation (Completata)
- [x] Setup progetto con uv e pyproject.toml
- [x] Configurazione con Pydantic Settings
- [x] Struttura API REST con FastAPI
- [x] Health check endpoints
- [x] Docker e docker-compose setup
- [x] Middleware di logging con request tracking
- [x] Documentazione API interattiva (Swagger/ReDoc)

### 🚧 Fase 2: Ingestion Pipeline (In Corso)
- [ ] ObsidianParser per markdown + frontmatter
- [ ] Supporto wikilinks e backlinks
- [ ] Text chunking (recursive, fixed, semantic)
- [ ] Integrazione embeddings (OpenAI/local)
- [ ] Connessione Qdrant vector store
- [ ] CLI per ingestion (`mneme-ingest`)
- [ ] Ingestion incrementale con tracking

### 📋 Fase 3: RAG Agent
- [ ] Setup Datapizza AI agent
- [ ] Custom retrieval logic
- [ ] System prompts per note Obsidian
- [ ] Implementazione endpoint `/chat`
- [ ] Gestione conversazioni e context
- [ ] Source citations nel response

### 🎨 Fase 4: Features Avanzate
- [ ] Supporto multi-LLM (OpenAI, Anthropic, Mistral)
- [ ] Embeddings locali con sentence-transformers
- [ ] Support per immagini nelle note
- [ ] Graph-based retrieval
- [ ] Webhook per sync automatica
- [ ] Frontend web UI
- [ ] Multi-vault support

### 🚀 Fase 5: Production
- [ ] Test suite completa
- [ ] CI/CD pipeline
- [ ] Monitoring e metriche
- [ ] Rate limiting
- [ ] Caching
- [ ] Plugin Obsidian nativo

---

## 🛠️ Tech Stack

- **[Datapizza AI](https://github.com/datapizza-labs/datapizza-ai)** - Framework RAG e Agent
- **FastAPI** - REST API framework
- **Qdrant** / **ChromaDB** - Vector database
- **OpenAI** / **Anthropic** - LLM providers
- **OpenTelemetry** - Observability
- **Pydantic** - Data validation

---

## 🤝 Contributing

Contributi benvenuti! Apri una issue o una pull request.

1. Fork del progetto
2. Crea un branch (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

---

## 📄 License

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per i dettagli.

---

## 🙏 Credits

- Built with [Datapizza AI](https://datapizza.tech/en/ai-framework/) 🍕
- Ispirato dalla community Obsidian
- Nome dal greco antico *Mneme* (Μνήμη), dea della memoria

---

## 📧 Contatti

- **Issues**: [GitHub Issues](https://github.com/tuousername/mneme/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/tuousername/mneme/discussions)

---

<p align="center">
  Made with 🧠 and ☕ 
</p>