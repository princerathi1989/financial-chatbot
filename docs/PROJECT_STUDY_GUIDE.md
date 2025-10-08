# Financial Chatbot – Complete Study Guide

This guide explains the entire project as if you'll be examined on it: what each module does, how control flows, how the app starts, why the backend is needed, and how to run and extend it.

---

## 1) What this project is

- **Goal**: A financial multi-agent chatbot that can ingest PDF documents, store searchable embeddings, and answer questions using RAG (retrieval-augmented generation), generate executive summaries, and create MCQs.
- **Key technologies**: FastAPI (backend API), LangChain + LangGraph (agent workflow), OpenAI (LLM + embeddings), Pinecone (vector store) with local fallback, Streamlit (frontend), Pydantic (models), Loguru (logging).

---

## 2) High-level architecture

- **Frontend**: `frontend/app.py` – Streamlit UI for document upload and chatting
- **Backend API**: `backend/uvicorn_app.py` – FastAPI app exposing endpoints:
  - Upload documents, chat, list/get/delete documents, stats, health
- **Agents & Workflow**: `backend/app/workflow/` – LangGraph workflow (`FinancialWorkflow`) routes requests to specific agents:
  - Q&A agent, Summarization agent, MCQ agent, Error handler
- **Vector Store**: `backend/app/storage/vector_store.py` – Pinecone (cloud) or local JSON fallback for embeddings + similarity search
- **Ingestion Pipeline**: `backend/app/ingestion/pipeline.py` – Parses PDF documents, produces text chunks and metadata stored to vector store
- **API Layer**: `backend/app/api/financial_chatbot.py` – Unified service class that handles requests to workflow + storage + ingestion
- **Configuration**: `backend/app/core/config.py` – Centralized settings via Pydantic
- **Schemas/Models**: `backend/app/models/schemas.py` – Pydantic request/response models used by the API

Note on imports: backend modules import using the package-qualified form `app.*` (e.g., `from app.core.config import settings`).

---

## 3) How the app starts

1) **Unified Launcher**: `start_chatbot.py` sets up PYTHONPATH and starts both backend and frontend
2) **Backend**: `backend/uvicorn_app.py` creates FastAPI app, ensures directories, configures LangSmith tracing, sets up CORS and logging
3) **Chatbot Instance**: `backend/app/api/financial_chatbot.py` creates `FinancialChatbot()` with workflow and ingestion pipeline
4) **Vector Store**: `backend/app/storage/vector_store.py` initializes Pinecone or local fallback with OpenAI embeddings
5) **Frontend**: Streamlit UI connects to backend API endpoints

---

## 4) Control flow end-to-end

### 4.1 Document upload
- Frontend calls `POST /upload/multiple` with PDF files
- FastAPI handler validates file type/size, calls `chatbot.upload_document(file_content, filename)`
- `FinancialChatbot.upload_document()`:
  - Uses `DocumentIngestionPipeline.process_document()` to parse PDF and create chunks
  - Stores document metadata in local `document_store`
  - Adds chunks to vector store (Pinecone or local) with metadata
  - Returns `DocumentUploadResponse` with document ID and processing status

### 4.2 Chat processing
- Frontend sends `POST /chat` with message and optional document ID
- `FinancialChatbot.process_chat_message()`:
  - Searches vector store for relevant chunks if document ID provided
  - Prepares context from search results
  - Creates `FinancialRequest` and passes to `FinancialWorkflow.process_request()`
  - Workflow routes to appropriate agent based on query analysis
  - Agent processes request and returns response with sources and metadata
  - Returns `ChatResponse` with agent type, response, and sources

### 4.3 Agent routing
- `FinancialWorkflow` analyzes the query to determine agent type:
  - **Q&A Agent**: General questions, analytics, KPIs
  - **Summarization Agent**: Summary requests, executive summaries
  - **MCQ Agent**: Quiz generation, question creation
- Each agent uses LangChain tools and prompts specific to their function
- All agents return structured responses with sources and metadata

---

## 5) Key modules explained

### 5.1 `backend/app/api/financial_chatbot.py`
- **Purpose**: Unified API layer handling all chatbot operations
- **Key methods**:
  - `process_chat_message()`: Main chat processing with optional document context
  - `upload_document()`: Document processing and storage
  - `get_document_info()`, `list_documents()`, `delete_document()`: Document management
  - `search_documents()`, `get_document_chunks()`: Document search and retrieval
- **Integration**: Connects FastAPI endpoints to workflow and storage layers

### 5.2 `backend/app/workflow/financial_workflow.py`
- **Purpose**: LangGraph workflow orchestrating multi-agent system
- **Components**:
  - `FinancialWorkflow`: Main workflow class with agent routing logic
  - `_route_decision()`: Determines which agent to use based on query analysis
  - Agent nodes: `_rag_agent_node()`, `_summarization_agent_node()`, `_mcq_agent_node()`
- **State Management**: Uses `FinancialState` to pass data between agents
- **Agent Types**: Q&A (`q&a`), Summarization (`summarization`), MCQ (`mcq`)

### 5.3 `backend/app/storage/vector_store.py`
- **Purpose**: Vector storage abstraction with Pinecone and local fallback
- **Key features**:
  - Automatic fallback from Pinecone to local storage
  - Document chunk storage with metadata
  - Similarity search across documents
  - Document management (add, delete, retrieve)
- **Storage Types**:
  - **Pinecone**: Cloud-based vector database (production)
  - **Local**: JSON-based storage (development/fallback)

### 5.4 `backend/app/ingestion/pipeline.py`
- **Purpose**: Document processing and chunking pipeline
- **Components**:
  - `DocumentIngestionPipeline`: Main processing class
  - `PDFProcessor`: PDF document processing with PyPDF2
  - Text chunking with configurable size and overlap
- **Output**: Document chunks with metadata for vector storage

### 5.5 `backend/app/core/config.py`
- **Purpose**: Centralized configuration management
- **Key settings**:
  - OpenAI API configuration
  - Pinecone settings
  - Vector store configuration
  - Agent parameters (chunk size, top-k results, etc.)
- **Environment**: Supports development and production configurations

---

## 6) Data flow and storage

### 6.1 Document Storage
- **Uploads**: Temporary staging in `backend/app/storage/uploads/`
- **Processing**: Temporary files in `backend/app/storage/temp/`
- **Vector Storage**: Pinecone index or local JSON files
- **Metadata**: Stored in `FinancialChatbot.document_store` (in-memory)

### 6.2 Vector Storage
- **Pinecone**: Cloud-based, production-ready
- **Local Fallback**: JSON files for development/testing
- **Chunks**: Text segments with metadata (filename, document ID, etc.)
- **Embeddings**: OpenAI text-embedding-ada-002 model

---

## 7) API endpoints

### 7.1 Document Management
- `POST /upload/multiple`: Upload PDF documents
- `GET /documents`: List all documents
- `GET /documents/{id}`: Get specific document info
- `DELETE /documents/{id}`: Delete document and associated data

### 7.2 Chat and Agents
- `POST /chat`: Send message to chatbot (auto-routing)
- `GET /agents/{agent_type}`: Get agent information
- `GET /stats`: Get system statistics

### 7.3 System
- `GET /`: API information
- `GET /health`: Health check

---

## 8) Frontend (Streamlit)

### 8.1 `frontend/app.py`
- **Purpose**: User interface for document upload and chat
- **Features**:
  - File upload for PDF documents
  - Chat interface with message history
  - Agent selection and display
  - Document management
- **Integration**: Communicates with backend via HTTP API

---

## 9) Running and deployment

### 9.1 Development
```bash
# Unified launcher (recommended)
python start_chatbot.py

# Manual start
uvicorn backend.uvicorn_app:app --reload
streamlit run frontend/app.py
```

### 9.2 Production
```bash
# Docker
docker build -t financial-chatbot .
docker run -p 8000:8000 --env-file .env financial-chatbot

# Docker Compose
docker-compose up -d
```

### 9.3 Environment Setup
- Copy `env.example` to `.env`
- Set required API keys (OpenAI, Pinecone)
- Configure vector store settings
- Set environment variables for production

---

## 10) Extension points

### 10.1 Adding new agents
1. Add agent type to `AgentType` enum in `schemas.py`
2. Create agent node in `financial_workflow.py`
3. Add routing logic in `_route_decision()`
4. Update frontend agent mapping

### 10.2 Adding new document types
1. Create processor in `pipeline.py`
2. Add to `DocumentIngestionPipeline`
3. Update file type validation

### 10.3 Custom vector stores
1. Implement interface in `vector_store.py`
2. Add configuration options
3. Update initialization logic

---

## 11) Key concepts to understand

- **LangGraph**: Workflow orchestration for multi-agent systems
- **RAG**: Retrieval-augmented generation for context-aware responses
- **Vector Embeddings**: Numerical representations of text for similarity search
- **Agent Routing**: Automatic selection of appropriate agent based on query analysis
- **Document Chunking**: Breaking documents into manageable pieces for processing
- **Pinecone**: Cloud vector database for scalable similarity search

This architecture provides a scalable, maintainable foundation for financial document processing and multi-agent chatbot functionality.