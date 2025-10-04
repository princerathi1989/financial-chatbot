# Multi-Agent Chatbot API Documentation

## Overview

The Multi-Agent Chatbot API provides a comprehensive interface for interacting with specialized AI agents that can process documents, answer questions, generate summaries, create quizzes, and perform analytics.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement proper API key authentication.

## Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Document Upload

#### POST /upload/pdf

Upload and process a PDF document.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "document_id": "doc_123456",
  "filename": "document.pdf",
  "document_type": "pdf",
  "status": "processed",
  "metadata": {
    "total_chunks": 25,
    "total_words": 5000,
    "file_size": 1024000
  }
}
```

#### POST /upload/csv

Upload and process a CSV document.

**Request:**
- Content-Type: `multipart/form-data`
- Body: CSV file

**Response:**
```json
{
  "document_id": "doc_789012",
  "filename": "data.csv",
  "document_type": "csv",
  "status": "processed",
  "metadata": {
    "total_rows": 1000,
    "total_columns": 10,
    "file_size": 512000
  }
}
```

### Chat Interface

#### POST /chat

Send a message to the multi-agent system.

**Request:**
```json
{
  "message": "What is the main topic of the document?",
  "agent_type": "rag",
  "document_id": "doc_123456",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "The main topic of the document is...",
  "agent_type": "rag",
  "sources": [
    {
      "type": "document",
      "document_id": "doc_123456",
      "chunk_id": "chunk_001"
    }
  ],
  "metadata": {
    "confidence": 0.95,
    "processing_time": 1.2
  }
}
```

### Agent Information

#### GET /agents/{agent_type}

Get information about a specific agent.

**Parameters:**
- `agent_type`: One of `rag`, `summarization`, `mcq`, `analytics`

**Response:**
```json
{
  "name": "RAG Agent",
  "description": "Question-answering over PDF documents using retrieval-augmented generation",
  "capabilities": [
    "Document Q&A",
    "Context retrieval",
    "Citation tracking"
  ],
  "input_requirements": [
    "PDF documents",
    "Natural language questions"
  ]
}
```

### Document Management

#### GET /documents

List all uploaded documents.

**Response:**
```json
[
  {
    "document_id": "doc_123456",
    "filename": "document.pdf",
    "file_type": "pdf",
    "status": "processed"
  }
]
```

#### GET /documents/{document_id}

Get information about a specific document.

**Response:**
```json
{
  "document_id": "doc_123456",
  "filename": "document.pdf",
  "file_type": "pdf",
  "status": "processed",
  "metadata": {
    "total_chunks": 25,
    "total_words": 5000,
    "total_characters": 30000
  }
}
```

#### DELETE /documents/{document_id}

Delete a document and its associated data.

**Response:**
```json
{
  "message": "Document doc_123456 deleted successfully"
}
```

### System Statistics

#### GET /stats

Get system statistics and status.

**Response:**
```json
{
  "total_documents": 10,
  "pdf_documents": 7,
  "csv_documents": 3,
  "vector_store": {
    "total_vectors": 250,
    "collection_size": "50MB"
  },
  "agents": {
    "rag": "active",
    "summarization": "active",
    "mcq": "active",
    "analytics": "active"
  }
}
```

## Agent Types

### RAG Agent (`rag`)

**Purpose:** Question-answering over PDF documents using retrieval-augmented generation.

**Capabilities:**
- Answer questions about uploaded PDF documents
- Provide citations and source references
- Context-aware responses based on document content

**Usage:**
```json
{
  "message": "What are the key findings in this report?",
  "agent_type": "rag",
  "document_id": "doc_123456"
}
```

### Summarization Agent (`summarization`)

**Purpose:** Create executive summaries with key quotes and citations.

**Capabilities:**
- Generate executive summaries
- Extract key quotes with context
- Provide document overviews

**Usage:**
```json
{
  "message": "Summarize this document",
  "agent_type": "summarization",
  "document_id": "doc_123456"
}
```

### MCQ Agent (`mcq`)

**Purpose:** Generate multiple choice questions with answers and rationales.

**Capabilities:**
- Create educational questions
- Provide answer options
- Include detailed rationales

**Usage:**
```json
{
  "message": "Generate quiz questions from this document",
  "agent_type": "mcq",
  "document_id": "doc_123456"
}
```

### Analytics Agent (`analytics`)

**Purpose:** Provide insights, KPIs, trends, and anomaly detection over CSV data.

**Capabilities:**
- Calculate key performance indicators
- Detect trends and patterns
- Identify anomalies in data
- Generate business insights

**Usage:**
```json
{
  "message": "Analyze the trends in this data",
  "agent_type": "analytics",
  "document_id": "doc_789012"
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input data
- `404`: Not Found - Document or resource not found
- `413`: Payload Too Large - File size exceeds limit
- `500`: Internal Server Error - Server-side error

### Example Error Responses

**File Size Exceeded:**
```json
{
  "error": "File size (60.5MB) exceeds maximum allowed size (50MB)",
  "code": "413"
}
```

**Document Not Found:**
```json
{
  "error": "Document not found",
  "code": "404"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement appropriate rate limiting based on your requirements.

## File Upload Limits

- **Maximum file size:** 50MB
- **Supported formats:** PDF, CSV
- **Processing timeout:** 5 minutes

## Examples

### Complete Workflow Example

1. **Upload a PDF document:**
```bash
curl -X POST "http://localhost:8000/upload/pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

2. **Ask a question about the document:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main topic of this document?",
    "agent_type": "rag",
    "document_id": "doc_123456"
  }'
```

3. **Generate a summary:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize this document",
    "agent_type": "summarization",
    "document_id": "doc_123456"
  }'
```

## SDK Examples

### Python SDK

```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload/pdf',
        files={'file': f}
    )
    document_id = response.json()['document_id']

# Ask question
response = requests.post(
    'http://localhost:8000/chat',
    json={
        'message': 'What is the main topic?',
        'agent_type': 'rag',
        'document_id': document_id
    }
)
print(response.json()['response'])
```

### JavaScript SDK

```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/upload/pdf', {
  method: 'POST',
  body: formData
});
const { document_id } = await uploadResponse.json();

// Ask question
const chatResponse = await fetch('/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'What is the main topic?',
    agent_type: 'rag',
    document_id: document_id
  })
});
const { response } = await chatResponse.json();
console.log(response);
```
