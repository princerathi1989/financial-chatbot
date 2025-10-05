### Financial Chatbot – Complete Study Guide

This guide explains the entire project as if you’ll be examined on it: what each module does, how control flows, how the app starts, why the backend is needed, and how to run and extend it.

---

## 1) What this project is

- **Goal**: A financial multi‑agent chatbot that can ingest documents (PDF, CSV), store searchable embeddings, and answer questions using RAG (retrieval‑augmented generation), generate executive summaries, and create MCQs.
- **Key technologies**: FastAPI (backend API), LangChain + LangGraph (agent workflow), OpenAI (LLM + embeddings), Pinecone (vector store) with local fallback, Streamlit (simple frontend), Pydantic (models), Loguru (logging).

---

## 2) High‑level architecture

- **Frontend**: `frontend/streamlit_app/app.py` – UI for document upload and chatting.
- **Backend API**: `backend/uvicorn_app.py` – FastAPI app exposing endpoints:
  - Upload documents, chat, list/get/delete documents, stats, health.
- **Agents & Workflow**: `backend/app/workflow/` – LangGraph workflow (`FinancialWorkflow`) routes requests to specific agents:
  - RAG agent, Summarization agent, MCQ agent, Error handler.
- **Vector Store**: `backend/app/storage/vector_store.py` – Pinecone (cloud) or a local JSON fallback for embeddings + similarity search.
- **Ingestion Pipeline**: `backend/app/ingestion/pipeline.py` – Parses PDF/CSV, produces text chunks and metadata stored to vector store.
- **API Layer for Chatbot**: `backend/app/api/langgraph_chatbot.py` (primary) and `enhanced_chatbot.py` (alt) – Thin service classes that glue requests to workflow + storage + ingestion.
- **Configuration**: `backend/app/core/config.py` – Centralized settings via Pydantic. `service_config.py` – environment profiles (Pinecone‑only).
- **Schemas/Models**: `backend/app/models/schemas.py` – Pydantic request/response models used by the API.

- Note on imports: backend modules import using the package-qualified form `app.*` (e.g., `from app.core.config import settings`).

---

## 3) How the app starts

1) You run the FastAPI application (e.g., `uvicorn`):
   - Entry point: `backend/uvicorn_app.py`
   - Ensures directories (`ensure_directories()`), configures LangSmith tracing if enabled, sets up CORS and logging, and registers routes.
2) A global chatbot instance is imported from `backend/app/api/langgraph_chatbot.py`:
   - `chatbot = LangGraphChatbot()` constructs the workflow and ingestion pipeline.
3) A global `vector_store` is created on import of `backend/app/storage/vector_store.py`:
   - Connects to Pinecone if available, else switches to local fallback. Sets up embeddings (OpenAI) and the index.
4) The FastAPI server serves endpoints. Frontend (Streamlit) or any HTTP client can call them.

---

## 4) Control flow end‑to‑end

### 4.1 Document upload
- Frontend calls `POST /upload/multiple` with PDFs/CSVs.
- FastAPI handler (`uvicorn_app.py`) validates type/size, then calls `chatbot.upload_document(file_content, filename)`.
- `LangGraphChatbot.upload_document()`:
  - Uses `DocumentIngestionPipeline.process_document()` to save the file and parse it.
  - PDF: `PDFProcessor` extracts text with PyPDF2, then chunks according to `settings.max_chunk_size` and `settings.chunk_overlap`.
  - CSV: `CSVProcessor` loads into pandas, analyzes columns, builds descriptive chunks (summary, per‑column info, sample rows).
  - The pipeline returns metadata including `document_id`, `chunks`, counts, etc.
  - If chunks exist, it calls `vector_store.add_document_chunks()` to embed and store vectors (Pinecone or local fallback).
  - Returns a `DocumentUploadResponse` with status and counts.

### 4.2 Chat question
- Frontend calls `POST /chat` with a `ChatRequest` (message, optional `agent_type`, optional `document_id`).
- FastAPI handler passes the request to `chatbot.process_chat_message()`.
- The chatbot builds a `FinancialRequest` and invokes `FinancialWorkflow.process_request()`.
- `FinancialWorkflow` (LangGraph):
  - Enters the `router` node which decides the agent (`rag` | `summarization` | `mcq`) based on keywords or explicit `agent_type`.
  - For `rag`:
    - Retrieves top‑k similar chunks via `vector_store.search_similar_chunks()` (can filter to a `document_id` or search all).
    - Builds a concise prompt (`_create_standard_prompt` or `_create_analytics_prompt` if analytics‑like query and CSVs present).
    - Calls the LLM (`ChatOpenAI`) to produce a short, focused answer.
    - Returns `response`, `sources` (snippets + metadata), and `metadata` (e.g., number of chunks, complexity, doc types).
  - For `summarization`:
    - Loads all chunks across documents, builds a single prompt to produce an executive summary and key quotes.
  - For `mcq`:
    - Loads all chunks and asks the LLM to generate N MCQs with answers and rationales.
  - The workflow returns a `FinancialResponse` which is converted to the API’s `ChatResponse`.

---

## 5) Why the backend is needed

- **Security & separation of concerns**: API keys (OpenAI, Pinecone) and embedding/index management must stay server‑side.
- **Document processing**: PDF text extraction, CSV parsing, and chunking are CPU/IO tasks handled reliably server‑side.
- **Vector search**: Pinecone operations and local fallback persist outside the browser; the backend abstracts these details.
- **Workflow orchestration**: LangGraph/LangChain agents, prompts, and routing live in Python with proper error handling and observability.
- **Consistent API**: Frontends (web, mobile, CLI) can share the same reliable HTTP API.

---

## 6) Key files and what they do

- `backend/uvicorn_app.py`
  - Creates FastAPI app, configures CORS/logging, declares endpoints:
    - `GET /` root info, `GET /health`, `POST /upload/multiple`, `POST /chat`, `GET /agents/{agent_type}`, `GET /documents`, `GET /documents/{id}`, `DELETE /documents/{id}`, `GET /stats`.
  - Boot lifecycle via `lifespan`; sets up directories and LangSmith.

- `backend/app/api/langgraph_chatbot.py`
  - `LangGraphChatbot` thin service: constructs `FinancialWorkflow` and `DocumentIngestionPipeline`, mediates calls between API handlers, ingestion, and vector store. Keeps simple in‑memory `document_store`.

- `backend/app/api/enhanced_chatbot.py`
  - Alternative variant that fetches context from the vector store by `document_id` and assembles a context header. Not the default wiring in `uvicorn_app.py` but useful as a reference.

- `backend/app/core/config.py`
  - Pydantic `Settings` with OpenAI/Pinecone models, vector store settings, directories, and agent parameters (e.g., `rag_top_k_results`, `mcq_num_questions`).
  - `ensure_directories()` creates upload/temp (and Chroma dir if chosen).
  - `setup_langsmith()` enables LangSmith tracing via env vars when a key is present.

- `backend/app/core/service_config.py`
  - Pinecone‑only service profiles for development/production, with validators and helper functions to switch/validate current setup.

- `backend/app/ingestion/pipeline.py`
  - `PDFProcessor`: extracts text with PyPDF2, chunks based on settings.
  - `CSVProcessor`: loads with pandas, analyzes schema and data, produces descriptive chunks.
  - `DocumentIngestionPipeline`: saves files to `settings.upload_directory`, assigns a UUID `document_id`, chooses processor, returns metadata.

- `backend/app/storage/vector_store.py`
  - Initializes embeddings (OpenAI) and Pinecone client/index; otherwise uses a local JSON fallback.
  - `add_document_chunks()`: embeds each chunk and upserts to Pinecone (or stores embeddings locally).
  - `search_similar_chunks()`: embeds the query and searches Pinecone (or cosine similarity over local data).
  - `get_document_chunks()`, `get_all_chunks()`, `delete_document()`, `get_collection_stats()` utility methods.

- `backend/app/workflow/financial_workflow.py`
  - Builds the LangGraph graph with nodes: `router`, `rag_agent`, `summarization_agent`, `mcq_agent`, `error_handler`.
  - RAG node picks analytics prompt if query contains analytics keywords and CSVs are present; otherwise standard prompt. Responses are intentionally concise.

- `backend/app/workflow/state.py`
  - TypedDict state schema and Pydantic request/response models (`FinancialRequest`, `FinancialResponse`) for the workflow layer.

- `backend/app/models/schemas.py`
  - API models: `ChatRequest`, `ChatResponse`, `DocumentUploadResponse`, plus enums like `AgentType`, `DocumentType`.

- `frontend/streamlit_app/app.py`
  - Simple UI for uploads and chatting against the FastAPI backend (refer to the code to see the exact endpoints it calls).

---

## 7) Request/response schemas (for exams)

- `ChatRequest`
  - `message: str`
  - `agent_type?: {rag|summarization|mcq}`
  - `document_id?: str` (optional context restriction)
  - `conversation_history?: ChatMessage[]` (optional)

- `ChatResponse`
  - `response: str` (LLM answer)
  - `agent_type: AgentType`
  - `sources?: List[ { content, metadata, relevance_score, document_type } ]`
  - `metadata?: Dict` (e.g., `context_chunks_found`, `is_analytics_query`, etc.)

- `DocumentUploadResponse`
  - `document_id: str`, `filename: str`, `document_type: {pdf|csv}`, `status: processed|error`, `metadata` (counts, sizes, errors)

---

## 8) How the vector store works

- On startup, a global `vector_store` is instantiated.
- If Pinecone client and API key are available, it creates/uses the configured index; otherwise uses a local JSON file store.
- On `add_document_chunks`, each chunk is embedded via OpenAI and stored:
  - Pinecone path: `upsert()` vectors with metadata (`document_id`, `chunk_index`, `content`, `chunk_length`).
  - Local fallback: store embeddings and metadata in a JSON file.
- On search, the query is embedded and a top‑k similarity search is run.

---

## 9) Error handling, logging, monitoring

- All major paths are wrapped in try/except and return user‑friendly messages.
- `uvicorn_app.py` defines global exception handlers to normalize errors into `ErrorResponse`.
- Logging via Loguru: structured messages, log level from settings, emits to stdout by default.
- Optional LangSmith tracing can be enabled by environment variables (`setup_langsmith()`).

---

## 10) Configuration and environment

- `backend/app/core/config.py` defines `Settings`, loaded from `.env`.
- Important variables (representative):
  - `OPENAI_API_KEY` (maps to `settings.openai_api_key`)
  - `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`
  - `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`
  - `RAG_TOP_K_RESULTS`, `MAX_CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_FILE_SIZE_MB`
  - `LANGSMITH_API_KEY` and related tracing values (optional)
- `ensure_directories()` guarantees upload and temp directories exist under `backend/app/storage`.

---

## 11) API endpoints to remember

- `GET /` – Service info.
- `GET /health` – Health check.
- `POST /upload/multiple` – Upload and process up to 10 PDF/CSV files.
- `POST /chat` – Send a message and get a response (RAG, summarization, or MCQ).
- `GET /agents/{agent_type}` – Static info about each agent.
- `GET /documents` – List uploaded documents (note: current in‑memory/placeholder listing, see chatbot used).
- `GET /documents/{document_id}` – Get document info.
- `DELETE /documents/{document_id}` – Delete a document and associated vectors.
- `GET /stats` – Aggregate counts + vector store stats.

---

## 12) How to run locally

1) Create and populate a `.env` with at least `OPENAI_API_KEY`. Add Pinecone keys to use cloud vectors; otherwise fallback is used.
2) Install backend requirements:
   - From repo root: `pip install -r backend/requirements.txt` (or use provided `venv`).
3) Start backend:
   - From repo root: `python -m uvicorn backend.uvicorn_app:app --reload --host 0.0.0.0 --port 8000`
4) Open docs: `http://localhost:8000/docs`.
5) Optionally run Streamlit UI:
   - From repo root: `streamlit run frontend/streamlit_app/app.py`

---

## 13) Common exam‑style questions (with brief answers)

- **Q: Where is routing to agents decided?**
  - In `backend/app/workflow/financial_workflow.py` inside the `router` node (`_router_node`) using keyword heuristics or explicit `agent_type`.

- **Q: What happens during document upload?**
  - Files are saved, parsed (PDF via PyPDF2, CSV via pandas), chunked, embedded, and stored in Pinecone/local fallback. A `DocumentUploadResponse` is returned.

- **Q: Why not do everything in the frontend?**
  - Security (keys), heavy processing (PDF/CSV parsing), and vector index management require a trusted server environment.

- **Q: How does RAG pick relevant context?**
  - It embeds the user query, runs vector similarity search to retrieve top‑k chunks, and feeds them into a concise prompt to the LLM.

- **Q: How are errors returned to clients?**
  - As structured JSON via `ErrorResponse` with appropriate HTTP status codes; unhandled exceptions are caught by global handlers.

- **Q: What are the agents supported?**
  - `rag` (Q&A/analytics), `summarization` (executive summary), `mcq` (question generation).

- **Q: Where are settings configured?**
  - `backend/app/core/config.py` with `.env` overrides. Directories, models, chunking, top‑k, ports, etc.

---

## 14) Extending the system

- Add new agent: create a new node in `FinancialWorkflow`, route to it from the `router`, and add its prompts and outputs.
- Swap vector store: extend `vector_store.py` to support another backend (e.g., Chroma/FAISS) and toggle via settings.
- Persist documents: replace the in‑memory `document_store` with a real database and add listing/querying methods.
- Improve frontend: build richer interactions in Streamlit or another framework; call the same backend endpoints.

---

## 15) Key takeaways

- Clear separation: UI ↔ API ↔ Workflow ↔ Storage.
- Robust ingestion for PDFs/CSVs; embeddings allow semantic retrieval.
- LangGraph orchestrates concise, exam‑friendly responses through specialized agents.
- Backend ensures security, performance, and consistent behavior across clients.


