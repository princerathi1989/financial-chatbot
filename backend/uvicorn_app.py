"""FastAPI application for the multi-agent chatbot."""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from loguru import logger
import sys
import os
from contextlib import asynccontextmanager

from app.core.config import settings, ensure_directories, setup_langsmith
from app.models.schemas import (
    ChatRequest, ChatResponse, DocumentUploadResponse, 
    ErrorResponse, AgentType, DocumentType
)
from app.api.langgraph_chatbot import chatbot

ensure_directories()

setup_langsmith()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Financial Multi-Agent Chatbot API")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"OpenAI model: {settings.openai_model}")
    yield
    logger.info("Shutting down Financial Multi-Agent Chatbot API")


app = FastAPI(
    title="Financial Multi-Agent Chatbot",
    description="A production-style POC for ingesting financial PDFs and CSVs with multi-agent capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.remove()
logger.add(sys.stdout, level=settings.log_level)




@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Financial Multi-Agent Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "agents": ["rag", "summarization", "mcq"],
        "supported_formats": ["pdf", "csv"]
    }


@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }


@app.post("/upload/multiple", response_model=List[DocumentUploadResponse])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload and process multiple documents (PDFs and CSVs)."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 10:  # Limit to 10 files at once
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        responses = []
        errors = []
        
        for file in files:
            try:
                # Validate file type
                if not file.filename.lower().endswith(('.pdf', '.csv')):
                    errors.append(f"{file.filename}: Only PDF and CSV files are allowed")
                    continue
                
                # Check file size
                file_content = await file.read()
                file_size_mb = len(file_content) / (1024 * 1024)
                if file_size_mb > settings.max_file_size_mb:
                    errors.append(f"{file.filename}: File size ({file_size_mb:.2f}MB) exceeds maximum ({settings.max_file_size_mb}MB)")
                    continue
                
                # Process the document
                response = chatbot.upload_document(file_content, file.filename)
                responses.append(response)
                
                logger.info(f"Successfully uploaded: {file.filename}")
                
            except Exception as e:
                logger.error(f"Error uploading {file.filename}: {e}")
                errors.append(f"{file.filename}: {str(e)}")
                responses.append(DocumentUploadResponse(
                    document_id="",
                    filename=file.filename,
                    document_type="unknown",
                    status='error',
                    metadata={"error": str(e)}
                ))
        
        # If all files failed, return error
        if not responses or all(r.status == 'error' for r in responses):
            raise HTTPException(status_code=500, detail=f"All uploads failed: {'; '.join(errors)}")
        
        logger.info(f"Batch upload completed: {len([r for r in responses if r.status == 'processed'])} successful, {len(errors)} errors")
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the multi-agent system."""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process the chat message
        response = chatbot.process_chat_message(request)
        
        logger.info(f"Processed chat message with {response.agent_type} agent")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_type}", response_model=dict)
async def get_agent_info(agent_type: AgentType):
    """Get information about a specific agent."""
    agent_info = {
        AgentType.RAG: {
            "name": "Universal Financial Agent",
            "description": "Question-answering and analytics over PDF and CSV documents using retrieval-augmented generation",
            "capabilities": ["Document Q&A", "Analytics & KPIs", "Trend analysis", "Context retrieval", "Citation tracking", "Data insights"],
            "input_requirements": ["PDF and CSV documents", "Natural language questions", "Analytics queries"]
        },
        AgentType.SUMMARIZATION: {
            "name": "Summarization Agent",
            "description": "Creates executive summaries with key quotes and citations",
            "capabilities": ["Executive summaries", "Key quote extraction", "Citation tracking"],
            "input_requirements": ["PDF documents"]
        },
        AgentType.MCQ: {
            "name": "MCQ Generation Agent",
            "description": "Generates multiple choice questions with answers and rationales",
            "capabilities": ["Question generation", "Answer validation", "Educational content"],
            "input_requirements": ["PDF documents", "Topic specification (optional)"]
        }
    }
    
    if agent_type not in agent_info:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    return agent_info[agent_type]


@app.get("/documents", response_model=List[dict])
async def list_documents():
    """List all uploaded documents."""
    try:
        documents = chatbot.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{document_id}", response_model=dict)
async def get_document(document_id: str):
    """Get information about a specific document."""
    try:
        doc_info = chatbot.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": document_id,
            "filename": doc_info["filename"],
            "file_type": doc_info["file_type"],
            "status": doc_info["status"],
            "metadata": {
                "total_chunks": doc_info.get("total_chunks", 0),
                "total_words": doc_info.get("total_words", 0),
                "total_characters": doc_info.get("total_characters", 0)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{document_id}", response_model=dict)
async def delete_document(document_id: str):
    """Delete a document and its associated data."""
    try:
        success = chatbot.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": f"Document {document_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=dict)
async def get_stats():
    """Get system statistics."""
    try:
        from app.storage.vector_store import vector_store
        
        documents = chatbot.list_documents()
        vector_stats = vector_store.get_collection_stats()
        
        return {
            "total_documents": len(documents),
            "pdf_documents": len([d for d in documents if d["file_type"] == "pdf"]),
            "csv_documents": len([d for d in documents if d["file_type"] == "csv"]),
            "vector_store": vector_stats,
            "agents": {
                "rag": "active",
                "summarization": "active", 
                "mcq": "active"
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            code="500"
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.uvicorn_app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        workers=settings.workers
    )

