# Multi-Agent Chatbot Development Guidelines

This document provides comprehensive guidelines for developing and maintaining the multi-agent chatbot system.

## Development Workflow

### 1. Setting Up Development Environment
```bash
# Clone the repository
git clone <repository-url>
cd multi-agent-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python main.py
```

### 2. Code Standards

#### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Use descriptive variable and function names
- Keep functions small and focused
- Use docstrings for all public functions and classes

#### Import Organization
```python
# Standard library imports
import os
import sys
from typing import List, Optional, Dict

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local imports
from core.config import settings
from agents.rag_agent import RAGAgent
```

#### Error Handling
```python
try:
    result = some_operation()
    return result
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. Agent Development

#### Creating a New Agent
1. Create agent file in `agents/` directory
2. Implement required methods:
   - `__init__(self, config: Settings)`
   - `process_query(self, message: str, document_id: Optional[str])`
   - `process_document(self, document_id: str)`
3. Add agent to `MultiAgentChatbot.agents` dictionary
4. Update `determine_agent_type()` method
5. Add processing logic in `process_chat_message()`
6. Create unit tests

#### Agent Interface
```python
class BaseAgent:
    def __init__(self, config: Settings):
        self.config = config
        self.logger = logger.bind(agent=self.__class__.__name__)
    
    def process_query(self, message: str, document_id: Optional[str] = None) -> ChatResponse:
        """Process a user query."""
        raise NotImplementedError
    
    def process_document(self, document_id: str) -> Any:
        """Process a specific document."""
        raise NotImplementedError
```

### 4. API Development

#### Endpoint Structure
```python
@app.post("/endpoint", response_model=ResponseModel)
async def endpoint_function(request: RequestModel):
    """Endpoint description."""
    try:
        # Implementation
        result = process_request(request)
        return ResponseModel(**result)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Request/Response Models
```python
class RequestModel(BaseModel):
    """Request model with validation."""
    field: str = Field(..., description="Field description", min_length=1)
    
    class Config:
        schema_extra = {
            "example": {
                "field": "example value"
            }
        }

class ResponseModel(BaseModel):
    """Response model."""
    result: str = Field(..., description="Result description")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
```

### 5. Testing Guidelines

#### Unit Testing
```python
import pytest
from unittest.mock import Mock, patch

class TestAgentFunctionality:
    @pytest.fixture
    def mock_dependencies(self):
        return {
            'vector_store': Mock(),
            'openai_client': Mock()
        }
    
    def test_agent_query_processing(self, mock_dependencies):
        # Arrange
        agent = RAGAgent(**mock_dependencies)
        
        # Act
        result = agent.process_query("test query")
        
        # Assert
        assert result.response is not None
        assert result.agent_type == AgentType.RAG
```

#### Integration Testing
```python
from fastapi.testclient import TestClient

def test_api_endpoint():
    client = TestClient(app)
    response = client.post("/chat", json={"message": "test message"})
    assert response.status_code == 200
    assert "response" in response.json()
```

### 6. Configuration Management

#### Environment Variables
```python
class Settings(BaseSettings):
    # Required settings
    openai_api_key: str
    
    # Optional settings with defaults
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

#### Configuration Validation
```python
@validator('openai_api_key')
def validate_api_key(cls, v):
    if not v or len(v) < 10:
        raise ValueError('API key must be at least 10 characters')
    return v
```

### 7. Logging Standards

#### Structured Logging
```python
import structlog
from loguru import logger

# Configure logger
logger = logger.bind(
    service="multi-agent-chatbot",
    version="1.0.0"
)

# Usage
logger.info("Processing request", 
           request_id=request_id,
           agent_type=agent_type,
           user_id=user_id)
```

#### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Something unexpected happened
- **ERROR**: A serious problem occurred
- **CRITICAL**: A very serious error occurred

### 8. Performance Optimization

#### Async Operations
```python
async def process_document_async(document_id: str):
    """Process document asynchronously."""
    tasks = [
        process_chunks_async(chunks),
        update_metadata_async(document_id),
        index_document_async(document_id)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_document_metadata(document_id: str):
    """Cache document metadata."""
    return fetch_metadata_from_db(document_id)
```

### 9. Security Best Practices

#### Input Validation
```python
def validate_file_upload(file: UploadFile):
    """Validate uploaded file."""
    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    return True
```

#### Secret Management
```python
# Use environment variables for secrets
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")
```

### 10. Deployment Guidelines

#### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=false
    volumes:
      - ./storage:/app/storage
```

## Troubleshooting

### Common Issues

1. **Agent Not Responding**
   - Check agent initialization
   - Verify configuration settings
   - Check logs for errors

2. **Vector Store Connection Issues**
   - Verify database connection
   - Check network connectivity
   - Validate configuration

3. **Document Processing Failures**
   - Check file format support
   - Verify file size limits
   - Check processing pipeline logs

4. **API Endpoint Errors**
   - Validate request format
   - Check authentication
   - Review error logs

### Debugging Tips

1. Use structured logging with correlation IDs
2. Enable debug mode for detailed logs
3. Use health check endpoints
4. Monitor system resources
5. Check external service status
