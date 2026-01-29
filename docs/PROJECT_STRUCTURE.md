# LegalRAG India Project Structure

```
legal-rag-india/
├── backend/                    # FastAPI backend
│   ├── main.py                # Entry point, FastAPI app
│   ├── config.py              # Configuration management
│   ├── models/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── request.py         # API request models
│   │   └── response.py        # API response models
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── llm_service.py     # LLM provider abstraction
│   │   ├── rag_service.py     # RAG pipeline
│   │   └── embedding_service.py # Embedding generation
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── query.py           # Legal query endpoints
│   │   └── search.py          # Case search endpoints
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── text_processing.py # Text cleaning, chunking
│
├── frontend/                  # Streamlit UI (MVP)
│   ├── app.py                # Main Streamlit app
│   └── components/           # Reusable UI components
│       └── __init__.py
│
├── data/                     # Data storage
│   ├── raw/                  # Raw scraped data (gitignored)
│   ├── processed/            # Processed, embedded data (gitignored)
│   └── sample/               # Sample data for testing
│
├── docs/                     # Documentation
│   ├── API.md               # API documentation
│   ├── ARCHITECTURE.md      # System architecture
│   └── DEPLOYMENT.md        # Deployment guide
│
├── tests/                    # Unit & integration tests
│   ├── __init__.py
│   ├── test_llm_service.py
│   └── test_rag_service.py
│
├── scripts/                  # Utility scripts
│   ├── scrape_judgments.py  # Data collection from Indian Kanoon
│   ├── generate_embeddings.py # Batch embedding generation
│   └── setup_vector_db.py   # Vector store initialization
│
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # Project overview
├── requirements.txt        # Python dependencies
└── LICENSE                 # MIT License
```

## Development Workflow

### Phase 1: MVP (Current)
1. ✅ Project setup
2. ⏳ Data pipeline (scrape 10K judgments)
3. ⏳ Embedding generation
4. ⏳ Basic RAG implementation
5. ⏳ Simple Streamlit UI

### Phase 2: Core Features
1. Multi-provider LLM routing
2. Citation verification
3. Multilingual support (Hindi)
4. User feedback system

### Phase 3: Production
1. React frontend
2. User authentication
3. Query analytics
4. Production deployment

## Quick Start Commands

```bash
# Backend development
cd backend
python main.py

# Frontend development
cd frontend
streamlit run app.py

# Run tests
pytest tests/

# Format code
black backend/ frontend/
ruff check backend/ frontend/
```
