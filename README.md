# Financial Multi-Agent Chatbot

A production-ready financial multi-agent chatbot that processes financial documents and answers questions using LangGraph + LangChain. Pinecone is the default vector store; Chroma is optional for local-only runs.

## Features

- Financial Q&A, summarization, MCQ generation, and analytics
- PDF/CSV ingestion with intelligent chunking
- Pinecone vector store (default) or optional local Chroma
- FastAPI backend + Streamlit UI
- Optional LangSmith tracing

## Tech Stack

- LangGraph, LangChain, FastAPI, Streamlit, OpenAI, Pydantic
- Vector Store: Pinecone (default). Chroma (optional/local)

## Quick Start

### Prerequisites
- Python 3.11+
- OPENAI_API_KEY (required)
- Pinecone API key (if using Pinecone, default)

### Install
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp env.example .env
```

### Run
- One command (backend + frontend, also clears uploads each start):
```bash
python start_chatbot.py
```

- API only:
```bash
export PYTHONPATH=$PWD/backend/app
uvicorn backend.uvicorn_app:app --reload --host 0.0.0.0 --port 8000
```

- Frontend only:
```bash
streamlit run frontend/app.py
```

Access: UI http://localhost:8501 • API docs http://localhost:8000/docs

## Project Structure
```
financial-chatbot/
├── backend/
│  ├── app/
│  │  ├── api/                 # FastAPI routers & chatbot APIs
│  │  ├── core/                # config/settings
│  │  ├── ingestion/           # document loaders/pipeline
│  │  ├── models/              # pydantic schemas
│  │  ├── storage/             # vector store + data dirs (uploads, temp)
│  │  └── workflow/            # LangGraph flows & state
│  ├── requirements.txt
│  └── uvicorn_app.py
├── frontend/
│  └── app.py
├── infra/
│  ├── deployment/
│  └── docker/
├── docs/
├── start_chatbot.py           # unified launcher (clears uploads on start)
├── env.example
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Configuration

Environment variables (examples in `.env`):

| Variable | Description | Default |
|---|---|---|
| OPENAI_API_KEY | OpenAI API key | required |
| VECTOR_STORE_TYPE | `pinecone` or `chroma` | pinecone |
| PINECONE_API_KEY | Pinecone API key | required if pinecone |
| PINECONE_ENVIRONMENT | Pinecone env (e.g., `us-east-1`) | us-east-1 |
| PINECONE_INDEX_NAME | Pinecone index | financial-documents |
| LOG_LEVEL | Logging level | INFO |

Notes:
- Storage paths resolve under `backend/app/storage/`.
- `uploads/` is a temporary staging area and is cleared on each start by the launcher.
- `chroma_db/` is only created if `VECTOR_STORE_TYPE=chroma`.
- Logs go to stdout (no `logs/` directory).

## API Examples
```bash
curl -X POST http://localhost:8000/upload/pdf \
  -H "Content-Type: multipart/form-data" \
  -F "file=@financial_report.pdf"

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Summarize the key financial highlights","agent_type":"summarization"}'
```

## Notes on Docker
Paths changed after the restructure; container files may need updates before use.

## License
MIT