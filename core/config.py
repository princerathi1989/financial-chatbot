"""Core configuration and settings for the financial multi-agent chatbot."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


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
    
    # Database Configuration
    chroma_persist_directory: str = "./storage/chroma_db"
    upload_directory: str = "./storage/uploads"
    
    # Production Cloud Configuration
    environment: str = "development"  # development, staging, production
    
    # Vector Store Configuration (Cloud alternatives)
    vector_store_type: str = "pinecone"  # chroma, pinecone, weaviate, qdrant, zilliz
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "financial-documents"
    pinecone_metric: str = "cosine"
    
    # Zilliz Cloud Configuration (cheapest option)
    zilliz_api_key: Optional[str] = None
    zilliz_cloud_region: str = "us-east-1"
    zilliz_collection_name: str = "financial_documents"
    zilliz_uri: Optional[str] = None
    zilliz_token: Optional[str] = None
    
    # Cloud Storage Configuration
    storage_type: str = "local"  # local, s3, gcs, azure
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None
    
    # Azure Blob Storage Configuration (cheapest option)
    azure_storage_account: Optional[str] = None
    azure_storage_key: Optional[str] = None
    azure_container_name: str = "financial-documents"
    azure_blob_tier: str = "Hot"  # Hot, Cool, Archive
    azure_blob_type: str = "BlockBlob"  # BlockBlob, PageBlob, AppendBlob
    
    # Database Configuration (for document metadata)
    database_type: str = "sqlite"  # sqlite, postgresql, mongodb
    database_url: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    
    # MongoDB Atlas Configuration (cheapest option)
    mongodb_connection_string: Optional[str] = None
    mongodb_database_name: str = "financial_chatbot"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()


def ensure_directories():
    """Ensure required directories exist."""
    os.makedirs(settings.chroma_persist_directory, exist_ok=True)
    os.makedirs(settings.upload_directory, exist_ok=True)
    os.makedirs("./storage/temp", exist_ok=True)


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

