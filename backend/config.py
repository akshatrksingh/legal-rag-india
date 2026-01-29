"""
Configuration management for LegalRAG India
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    groq_api_key: str = ""
    together_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    # LLM Configuration
    primary_llm_provider: str = "groq"
    primary_llm_model: str = "llama-3.3-70b-versatile"
    
    # Embedding Configuration
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_device: str = "cpu"  # or "cuda" if GPU available
    
    # Vector Store
    vector_store_type: str = "faiss"
    vector_store_path: str = "../data/processed/vector_store"
    
    # Database
    mongodb_uri: str = "mongodb://localhost:27017/legal-rag-india"
    
    # Application
    environment: str = "development"
    debug: bool = True
    
    # API Limits
    max_query_length: int = 1000
    max_results: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
