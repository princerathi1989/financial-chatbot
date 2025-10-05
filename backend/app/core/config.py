"""Core configuration and settings for the financial multi-agent chatbot."""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # LangSmith Configuration (Optional)
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "financial-chatbot"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langchain_tracing_v2: Optional[str] = None
    
    # Storage directories (resolved relative to backend/app/storage)
    # Compute base as backend/app/storage regardless of CWD
    _storage_base_dir: Path = Path(__file__).resolve().parents[1] / "storage"
    chroma_persist_directory: str = str((_storage_base_dir / "chroma_db").resolve())
    upload_directory: str = str((_storage_base_dir / "uploads").resolve())
    temp_directory: str = str((_storage_base_dir / "temp").resolve())
    
    # Production Cloud Configuration
    environment: str = "development"  # development, staging, production
    
    # Vector Store Configuration (Pinecone only)
    vector_store_type: str = "pinecone"  # pinecone only
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "financial-documents"
    pinecone_metric: str = "cosine"
    
    # Database Configuration (for document metadata - in-memory only)
    database_type: str = "memory"  # memory only for session-based processing
    
    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    max_file_size_mb: int = 50
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Production Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    workers: int = 1
    reload: bool = False
    
    # Agent Settings
    rag_top_k_results: int = 5
    summary_max_length: int = 500
    mcq_num_questions: int = 5
    analytics_confidence_threshold: float = 0.8
    
    # Document Processing Settings
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()


def ensure_directories():
    """Ensure required directories exist."""
    # Always ensure upload and temp directories
    os.makedirs(settings.upload_directory, exist_ok=True)
    os.makedirs(settings.temp_directory, exist_ok=True)
    # Only create Chroma directory when Chroma is the selected vector store
    if settings.vector_store_type.lower() == "chroma":
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)


def setup_langsmith():
    """Setup LangSmith tracing if API key is provided."""
    if settings.langsmith_api_key:
        # Set environment variables for LangChain tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint
        print(f"LangSmith tracing enabled for project: {settings.langsmith_project}")
    else:
        print("LangSmith tracing disabled - no API key provided")

