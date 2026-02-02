"""
LegalRAG India Backend - Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

from rag_service import RAGService

app = FastAPI(
    title="LegalRAG India API",
    description="AI-Powered Legal Research Assistant for Indian Law",
    version="0.1.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class AskRequest(BaseModel):
    query: str
    top_k: int = 3

# Initialize RAG service (lazy loading)
rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    """Lazy load RAG service"""
    global rag_service
    if rag_service is None:
        print("Initializing RAG service...")
        rag_service = RAGService()
    return rag_service

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LegalRAG India API",
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        rag = get_rag_service()
        vector_stats = rag.vector_store.get_stats()
        
        return {
            "status": "healthy",
            "components": {
                "api": "operational",
                "llm": "operational",
                "vector_db": "operational",
                "total_documents": vector_stats.get("total_documents", 0)
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "components": {
                "api": "operational",
                "llm": "error",
                "vector_db": "error"
            },
            "error": str(e)
        }

@app.post("/search")
async def search(request: SearchRequest):
    """
    Semantic search over legal documents
    Returns top-k most relevant cases without LLM generation
    """
    try:
        rag = get_rag_service()
        results = rag.retrieve_documents(request.query, top_k=request.top_k)
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(request: AskRequest):
    """
    Ask a legal question - uses RAG to generate answer with citations
    """
    try:
        rag = get_rag_service()
        response = rag.ask(request.query, top_k=request.top_k)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )