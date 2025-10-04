"""Flexible service configuration system for easy switching between providers."""

from typing import Dict, Any, Optional
from enum import Enum
from loguru import logger
from core.config import settings


class ServiceProvider(Enum):
    """Available service providers for each component."""
    
    # Vector Stores
    CHROMA = "chroma"
    PINECONE = "pinecone"
    ZILLIZ = "zilliz"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    
    # Storage
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"
    
    # Databases
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


class ServiceConfiguration:
    """Service configuration manager for easy provider switching."""
    
    # Predefined configurations for different use cases
    CONFIGURATIONS = {
        "development": {
            "vector_store": ServiceProvider.CHROMA,
            "storage": ServiceProvider.LOCAL,
            "database": ServiceProvider.SQLITE,
            "description": "Local development setup - no cloud costs"
        },
        
        "budget": {
            "vector_store": ServiceProvider.ZILLIZ,
            "storage": ServiceProvider.AZURE,
            "database": ServiceProvider.MONGODB,
            "description": "Ultra-budget cloud setup - ~$7-17/month"
        },
        
        "standard": {
            "vector_store": ServiceProvider.PINECONE,
            "storage": ServiceProvider.S3,
            "database": ServiceProvider.POSTGRESQL,
            "description": "Standard production setup - ~$70-100/month"
        },
        
        "enterprise": {
            "vector_store": ServiceProvider.WEAVIATE,
            "storage": ServiceProvider.GCS,
            "database": ServiceProvider.POSTGRESQL,
            "description": "Enterprise-grade setup - ~$100-200/month"
        }
    }
    
    @classmethod
    def get_configuration(cls, config_name: str) -> Dict[str, Any]:
        """Get predefined configuration by name."""
        if config_name not in cls.CONFIGURATIONS:
            available = ", ".join(cls.CONFIGURATIONS.keys())
            raise ValueError(f"Unknown configuration '{config_name}'. Available: {available}")
        
        return cls.CONFIGURATIONS[config_name]
    
    @classmethod
    def list_configurations(cls) -> Dict[str, str]:
        """List all available configurations with descriptions."""
        return {name: config["description"] for name, config in cls.CONFIGURATIONS.items()}
    
    @classmethod
    def apply_configuration(cls, config_name: str) -> None:
        """Apply a predefined configuration to settings."""
        config = cls.get_configuration(config_name)
        
        # Update vector store
        settings.vector_store_type = config["vector_store"].value
        
        # Update storage
        settings.storage_type = config["storage"].value
        
        # Update database
        settings.database_type = config["database"].value
        
        logger.info(f"Applied '{config_name}' configuration: {config['description']}")
    
    @classmethod
    def get_current_configuration(cls) -> Dict[str, Any]:
        """Get current configuration based on settings."""
        return {
            "vector_store": settings.vector_store_type,
            "storage": settings.storage_type,
            "database": settings.database_type,
            "environment": settings.environment
        }
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate current configuration and return status."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "services": {}
        }
        
        # Validate vector store
        vector_store_status = cls._validate_vector_store()
        validation_result["services"]["vector_store"] = vector_store_status
        
        # Validate storage
        storage_status = cls._validate_storage()
        validation_result["services"]["storage"] = storage_status
        
        # Validate database
        database_status = cls._validate_database()
        validation_result["services"]["database"] = database_status
        
        # Check for errors
        for service, status in validation_result["services"].items():
            if not status["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(status["errors"])
            validation_result["warnings"].extend(status.get("warnings", []))
        
        return validation_result
    
    @classmethod
    def _validate_vector_store(cls) -> Dict[str, Any]:
        """Validate vector store configuration."""
        status = {"valid": True, "errors": [], "warnings": []}
        
        vector_store_type = settings.vector_store_type.lower()
        
        if vector_store_type == "pinecone":
            if not settings.pinecone_api_key:
                status["valid"] = False
                status["errors"].append("Pinecone API key is required")
        elif vector_store_type == "zilliz":
            if not settings.zilliz_api_key:
                status["valid"] = False
                status["errors"].append("Zilliz API key is required")
        elif vector_store_type == "chroma":
            status["warnings"].append("ChromaDB is not suitable for production deployment")
        
        return status
    
    @classmethod
    def _validate_storage(cls) -> Dict[str, Any]:
        """Validate storage configuration."""
        status = {"valid": True, "errors": [], "warnings": []}
        
        storage_type = settings.storage_type.lower()
        
        if storage_type == "s3":
            if not settings.aws_access_key_id or not settings.aws_secret_access_key:
                status["valid"] = False
                status["errors"].append("AWS credentials are required for S3")
            if not settings.s3_bucket_name:
                status["valid"] = False
                status["errors"].append("S3 bucket name is required")
        elif storage_type == "azure":
            if not settings.azure_storage_account or not settings.azure_storage_key:
                status["valid"] = False
                status["errors"].append("Azure Storage credentials are required")
        elif storage_type == "local":
            status["warnings"].append("Local storage is not suitable for production deployment")
        
        return status
    
    @classmethod
    def _validate_database(cls) -> Dict[str, Any]:
        """Validate database configuration."""
        status = {"valid": True, "errors": [], "warnings": []}
        
        database_type = settings.database_type.lower()
        
        if database_type == "postgresql":
            if not settings.database_url and not all([
                settings.postgres_host, settings.postgres_user, 
                settings.postgres_password, settings.postgres_db
            ]):
                status["valid"] = False
                status["errors"].append("PostgreSQL connection details are required")
        elif database_type == "mongodb":
            if not settings.mongodb_connection_string:
                status["valid"] = False
                status["errors"].append("MongoDB connection string is required")
        elif database_type == "sqlite":
            status["warnings"].append("SQLite is not suitable for production deployment")
        
        return status


class ServiceSwitcher:
    """Utility class for switching between service providers."""
    
    @staticmethod
    def switch_to_budget_config() -> None:
        """Switch to budget configuration (cheapest option)."""
        ServiceConfiguration.apply_configuration("budget")
        logger.info("Switched to budget configuration - cheapest cloud setup")
    
    @staticmethod
    def switch_to_production_config() -> None:
        """Switch to production configuration."""
        ServiceConfiguration.apply_configuration("standard")
        logger.info("Switched to production configuration")
    
    @staticmethod
    def switch_to_development_config() -> None:
        """Switch to development configuration (local)."""
        ServiceConfiguration.apply_configuration("development")
        logger.info("Switched to development configuration - local setup")
    
    @staticmethod
    def get_cost_estimate() -> Dict[str, Any]:
        """Get cost estimate for current configuration."""
        current_config = ServiceConfiguration.get_current_configuration()
        
        cost_estimates = {
            "vector_store": {
                "chroma": {"cost": "$0", "description": "Free (local)"},
                "zilliz": {"cost": "$0-50", "description": "Free tier + pay-as-you-go"},
                "pinecone": {"cost": "$70", "description": "Standard plan"},
                "weaviate": {"cost": "$25-100", "description": "Cloud plan"},
                "qdrant": {"cost": "$25-75", "description": "Cloud plan"}
            },
            "storage": {
                "local": {"cost": "$0", "description": "Free (local)"},
                "azure": {"cost": "$0-10", "description": "Free tier + usage"},
                "s3": {"cost": "$5-20", "description": "Standard storage"},
                "gcs": {"cost": "$5-20", "description": "Standard storage"}
            },
            "database": {
                "sqlite": {"cost": "$0", "description": "Free (local)"},
                "mongodb": {"cost": "$0-25", "description": "Free tier + usage"},
                "postgresql": {"cost": "$15-50", "description": "Managed service"}
            }
        }
        
        total_cost = "Unknown"
        if current_config["vector_store"] in cost_estimates["vector_store"]:
            vector_cost = cost_estimates["vector_store"][current_config["vector_store"]]["cost"]
            storage_cost = cost_estimates["storage"][current_config["storage"]]["cost"]
            database_cost = cost_estimates["database"][current_config["database"]]["cost"]
            
            # Simple cost calculation (this could be more sophisticated)
            if "$0" in [vector_cost, storage_cost, database_cost]:
                total_cost = "Free tier available"
            else:
                total_cost = f"~${vector_cost}-{storage_cost}-{database_cost}/month"
        
        return {
            "current_configuration": current_config,
            "cost_breakdown": {
                "vector_store": cost_estimates["vector_store"].get(current_config["vector_store"], {}),
                "storage": cost_estimates["storage"].get(current_config["storage"], {}),
                "database": cost_estimates["database"].get(current_config["database"], {})
            },
            "total_estimated_cost": total_cost
        }


# Convenience functions for easy configuration switching
def use_budget_setup():
    """Switch to budget setup (cheapest option)."""
    ServiceSwitcher.switch_to_budget_config()

def use_production_setup():
    """Switch to production setup."""
    ServiceSwitcher.switch_to_production_config()

def use_development_setup():
    """Switch to development setup (local)."""
    ServiceSwitcher.switch_to_development_config()

def validate_current_setup():
    """Validate current setup and return status."""
    return ServiceConfiguration.validate_configuration()

def get_cost_estimate():
    """Get cost estimate for current setup."""
    return ServiceSwitcher.get_cost_estimate()
