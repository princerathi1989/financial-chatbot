# Financial Multi-Agent Chatbot

A production-ready financial multi-agent chatbot that processes PDF documents and answers questions using LangGraph + LangChain with Pinecone vector store.

## Features

- **Multi-Agent System**: Q&A, Summarization, and MCQ generation agents
- **PDF Document Processing**: Intelligent chunking and ingestion
- **Pinecone Vector Store**: Cloud-based vector storage with local fallback
- **Modern UI**: FastAPI backend + Streamlit frontend
- **Production Ready**: Docker support, health checks, and monitoring

## Tech Stack

- **Backend**: FastAPI, LangGraph, LangChain, OpenAI, Pydantic
- **Frontend**: Streamlit
- **Vector Store**: Pinecone (primary), Local JSON (fallback)
- **AI**: OpenAI GPT models for text processing

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key (required)
- Pinecone API key (required for cloud storage)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd financial-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your API keys
```

### Running the Application

#### Option 1: Unified Launcher (Recommended)
```bash
python start_chatbot.py
```
This starts both backend (port 8000) and frontend (port 8501).

#### Option 2: Backend Only
```bash
python start_chatbot.py --no-frontend
```

#### Option 3: Manual Start
```bash
# Backend
export PYTHONPATH=$PWD/backend
uvicorn backend.uvicorn_app:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
streamlit run frontend/app.py --server.port 8501
```

### Access Points
- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Project Structure
```
financial-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/                    # Unified API layer
│   │   │   └── financial_chatbot.py
│   │   ├── core/                   # Configuration and settings
│   │   │   ├── config.py
│   │   │   └── service_config.py
│   │   ├── ingestion/              # Document processing pipeline
│   │   │   └── pipeline.py
│   │   ├── models/                 # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── storage/                # Vector store and data directories
│   │   │   ├── vector_store.py
│   │   │   ├── uploads/            # Temporary file storage
│   │   │   ├── temp/              # Processing temp files
│   │   │   └── chroma_db/         # Local Chroma database
│   │   └── workflow/              # LangGraph workflow and agents
│   │       ├── financial_workflow.py
│   │       └── state.py
│   └── uvicorn_app.py             # FastAPI application entry point
├── frontend/
│   └── app.py                     # Streamlit UI
├── docs/                          # Documentation
├── start_chatbot.py              # Unified application launcher
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml           # Docker Compose setup
├── env.example                  # Environment variables template
└── README.md                    # This file
```

## Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `PINECONE_API_KEY` | Pinecone API key | - | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `us-east-1` | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | `financial-documents` | No |
| `VECTOR_STORE_TYPE` | Storage type (`pinecone` or `local`) | `pinecone` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Environment (`development` or `production`) | `development` | No |

### Storage Configuration

- **Pinecone**: Cloud-based vector storage (recommended for production)
- **Local**: JSON-based fallback storage (development/testing)
- **Uploads**: Temporary staging area (cleared on each restart)
- **Chroma**: Optional local database (if using Chroma)

## API Usage

### Upload Documents
```bash
curl -X POST http://localhost:8000/upload/multiple \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Chat with Agents
```bash
# Q&A Agent (default)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the key financial highlights?"}'

# Summarization Agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize the document", "agent_type": "summarization"}'

# MCQ Agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate quiz questions", "agent_type": "mcq"}'
```

### Get Document Information
```bash
# List all documents
curl http://localhost:8000/documents

# Get specific document
curl http://localhost:8000/documents/{document_id}

# Get statistics
curl http://localhost:8000/stats
```

## Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t financial-chatbot .

# Run with environment file
docker run -p 8000:8000 --env-file .env financial-chatbot
```

### Docker Compose
```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Stop
docker-compose down
```

## Agent Types

### Q&A Agent
- **Purpose**: Question answering and analytics
- **Capabilities**: Document Q&A, analytics & KPIs, trend analysis
- **Input**: Natural language questions, analytics queries

### Summarization Agent
- **Purpose**: Document summarization
- **Capabilities**: Executive summaries, key quote extraction
- **Input**: PDF documents

### MCQ Agent
- **Purpose**: Multiple choice question generation
- **Capabilities**: Quiz creation, answer validation
- **Input**: PDF documents

## Development

### Code Quality
```bash
# Format code
black backend/app/ --line-length=100

# Lint code
flake8 backend/app/ --max-line-length=100

# Type checking
mypy backend/app/
```

### Testing
```bash
# Run tests (if available)
pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **Vector Store Connection**: Ensure Pinecone API key is correct
2. **OpenAI API**: Verify API key and sufficient credits
3. **File Uploads**: Check file permissions and disk space
4. **Port Conflicts**: Ensure ports 8000 and 8501 are available

### Logs
- Application logs are output to stdout
- Use `docker-compose logs -f chatbot` for Docker logs
- Check `/health` endpoint for service status

## License

MIT License - see LICENSE file for details.