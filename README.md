# LegalRAG India 🏛️

**AI-Powered Legal Research Assistant for Indian Law**

> Semantic search and AI-powered analysis over 1.4M+ Indian court judgments using Retrieval-Augmented Generation (RAG).

## 🎯 Problem Statement

India has 50M+ pending cases and citizens struggle to:
- Afford lawyers for simple legal questions
- Understand complex legal language
- Find relevant case precedents
- Know their rights and procedures

## 💡 Solution

NyayaSahayak uses Retrieval-Augmented Generation (RAG) to:
- Search 1.4M+ verified court judgments (Supreme Court, High Courts, Tribunals)
- Provide plain-language explanations in English and Hindi
- Cite verified legal precedents (no hallucinations)
- Guide users through legal procedures

## 🏗️ Architecture

```
User Query
    ↓
FastAPI Backend
    ↓
┌────────────┬─────────────┬──────────────┐
│   RAG      │  Vector DB  │   LLM        │
│ Pipeline   │  (FAISS)    │  (Groq)      │
└────────────┴─────────────┴──────────────┘
         ↓
    Verified Response with Citations
```

## 🛠️ Tech Stack

- **LLM**: Groq (Llama 3.3 70B) - 14.4K requests/day, free
- **Embeddings**: bge-large-en-v1.5 (open-source)
- **Vector DB**: FAISS (local, fast)
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit → React (planned)
- **Data**: Indian Kanoon API (1.4M+ judgments)
- **Deploy**: Render (free tier)

**Total Cost: $0/month** ✅

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Git
- Groq API key (free at groq.com)

### Installation

```bash
# Clone repository
git clone https://github.com/akshatrksingh/legal-rag-india.git
cd legal-rag-india

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run backend
cd backend
python main.py

# Run frontend (in another terminal)
cd frontend
streamlit run app.py
```

## 📊 Project Status

- [x] Project setup
- [ ] Data pipeline (Indian Kanoon API)
- [ ] Embedding generation
- [ ] Vector store setup (FAISS)
- [ ] RAG implementation
- [ ] FastAPI backend
- [ ] Streamlit UI
- [ ] Deployment
- [ ] Documentation

## 🎓 Background

Built by Akshat Singh (NYU MS CS) as a portfolio project demonstrating:
- RAG implementation at scale
- Multi-provider LLM orchestration
- Production-ready API design
- Domain-specific AI applications

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

## 📧 Contact

- LinkedIn: [linkedin.com/in/axatsngh](https://linkedin.com/in/axatsngh)
- GitHub: [@akshatrksingh](https://github.com/akshatrksingh)
- Email: as20255@nyu.edu

---

**Note**: This is a legal research tool, NOT legal advice. Always consult a qualified lawyer for legal matters.
