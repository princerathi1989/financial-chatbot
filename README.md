# Financial Multi-Agent Chatbot

A production-ready financial multi-agent chatbot system that processes financial documents and provides intelligent responses using LangGraph workflow orchestration with LangChain agents and LangSmith tracing.

## Features

- **Financial RAG Agent**: Question-answering over financial PDFs (10-K reports, earnings calls, financial statements) using LangChain retrievers
- **Financial Summarization Agent**: Creates executive summaries with key financial quotes and citations using LangChain chains
- **Financial MCQ Agent**: Generates multiple choice questions for financial knowledge assessment using LangChain tools
- **Financial Analytics Agent**: Provides insights, KPIs, trends, and anomaly detection over financial CSV data using LangChain tools
- **Document Processing**: Supports financial PDF and CSV uploads with intelligent chunking using LangChain document loaders
- **Vector Storage**: ChromaDB integration with LangChain for efficient financial document retrieval
- **LangSmith Integration**: Comprehensive tracing and monitoring of financial agent operations
- **RESTful API**: FastAPI-based API with comprehensive financial document analysis capabilities
- **Modern Web UI**: WhatsApp-like Streamlit interface for easy interaction

## Technology Stack

- **LangGraph**: Multi-agent workflow orchestration with state management
- **LangChain**: Agent framework, tools, chains, and document processing
- **LangSmith**: Tracing, monitoring, and debugging of financial agent operations
- **OpenAI**: GPT models for financial analysis and Q&A
- **ChromaDB**: Vector database for financial document storage
- **FastAPI**: REST API framework
- **Streamlit**: Modern web UI framework
- **Pydantic**: Data validation and serialization

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- LangSmith API key (optional, for tracing)
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key and LangSmith API key
   ```

5. **Run the application**
   
   **Option A: Start both UI and API together**
   ```bash
   python start_chatbot.py
   ```
   
   **Option B: Start API only**
   ```bash
   python main.py
   ```
   
   **Option C: Start UI only (requires API to be running)**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Access the application**
   - **Web UI**: http://localhost:8501 (WhatsApp-like interface)
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Usage

### Web UI (Recommended)

The easiest way to interact with the chatbot is through the modern WhatsApp-like web interface:

1. **Start the application**: `python start_chatbot.py`
2. **Open your browser**: Go to http://localhost:8501
3. **Select an agent**: Choose from RAG, Summarization, MCQ, or Analytics
4. **Upload documents**: Drag and drop PDF or CSV files
5. **Start chatting**: Type your questions and get instant responses

### API Usage

### Upload Financial Documents

```bash
# Upload a financial PDF (10-K report, earnings call, etc.)
curl -X POST "http://localhost:8000/upload/pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@financial_report.pdf"

# Upload financial CSV data (market data, trading data, etc.)
curl -X POST "http://localhost:8000/upload/csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@market_data.csv"
```

### Chat with Financial Agents

```bash
# Ask financial questions using RAG agent
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What was the company revenue growth rate in Q3?",
    "agent_type": "rag",
    "document_id": "doc_123456"
  }'

# Generate financial summary
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the key financial highlights",
    "agent_type": "summarization",
    "document_id": "doc_123456"
  }'

# Generate financial quiz questions
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate quiz questions about financial ratios",
    "agent_type": "mcq",
    "document_id": "doc_123456"
  }'

# Analyze financial data
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the trend in revenue and identify anomalies",
    "agent_type": "analytics",
    "document_id": "doc_789012"
  }'
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

This project uses **LangGraph** for workflow orchestration, providing:

- **State Management**: Centralized state handling across all agents
- **Workflow Routing**: Intelligent routing between RAG, Summarization, MCQ, and Analytics agents
- **Error Handling**: Comprehensive error handling and recovery
- **Tracing**: Full workflow tracing with LangSmith integration
- **Scalability**: Easy to extend with new agents and workflows

### LangGraph Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Router    │───▶│ RAG Agent   │    │ Summarization│
│   Node      │    │   Node      │    │   Agent     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ MCQ Agent   │    │ Analytics   │    │   Error     │
│   Node      │    │   Agent     │    │  Handler    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Project Structure

```
multi-agent-chatbot/
├── workflow/                  # LangGraph workflow implementation
│   ├── __init__.py
│   ├── financial_workflow.py  # Main workflow with all agents
│   └── state.py              # State management
├── api/                       # Simplified API layer
│   └── langgraph_chatbot.py   # LangGraph-based chatbot
├── core/                      # Core functionality
│   ├── config.py             # Configuration management
│   └── service_config.py     # Service configurations
├── ingestion/                 # Document processing
│   └── pipeline.py           # Document ingestion pipeline
├── storage/                   # Storage implementations
│   ├── vector_store.py       # Vector store implementation
│   ├── cloud_vector_store.py # Cloud vector store
│   ├── cloud_storage.py      # Cloud storage
│   └── cloud_database.py     # Cloud database
├── models/                    # Data models
│   └── schemas.py            # Pydantic schemas
├── docs/                      # Documentation
├── deployment/                # Deployment configurations
├── tests/                     # Test suites
├── main.py                    # Application entry point
├── streamlit_app.py          # Streamlit UI
├── start_chatbot.py          # Startup script
├── requirements.txt           # Dependencies
├── env.example               # Environment template
├── deploy-production.sh      # Production deployment script
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
└── README.md                 # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Adding New Agents

1. Add a new node to the LangGraph workflow in `workflow/financial_workflow.py`
2. Implement the agent logic as a node function
3. Add routing logic in the `_router_node` method
4. Add the new agent to the conditional edges
5. Update the state model if needed
6. Add tests

See the workflow implementation for examples of how to add new agents.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_FILE_SIZE_MB` | Maximum file size | `50` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB directory | `./storage/chroma_db` |
| `UPLOAD_DIRECTORY` | Upload directory | `./storage/uploads` |

### Agent Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `RAG_TOP_K_RESULTS` | Number of top results for RAG | `5` |
| `SUMMARY_MAX_LENGTH` | Maximum summary length | `500` |
| `MCQ_NUM_QUESTIONS` | Number of MCQ questions | `5` |
| `ANALYTICS_CONFIDENCE_THRESHOLD` | Analytics confidence threshold | `0.8` |

## Deployment

### Docker

```bash
# Build image
docker build -t multi-agent-chatbot .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-api-key \
  multi-agent-chatbot
```

### Kubernetes

See [Docker Configuration](deployment/DOCKER_CONFIGURATION.md) for Kubernetes deployment instructions.

## Monitoring

The application includes built-in monitoring capabilities:

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- System statistics: `/stats`

### Prometheus Integration

Metrics are exposed in Prometheus format for monitoring and alerting.

### Grafana Dashboards

Pre-configured dashboards are available in the `monitoring/dashboards/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue in the repository
- Check the documentation in the `docs/` directory
- Review the API documentation at `/docs`

## Roadmap

- [ ] Authentication and authorization
- [ ] Multi-tenant support
- [ ] Advanced analytics features
- [ ] Custom agent creation interface
- [ ] Real-time collaboration features
- [ ] Mobile application
- [ ] Advanced monitoring and alerting