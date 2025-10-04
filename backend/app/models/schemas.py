"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class AgentType(str, Enum):
    """Available agent types."""
    QnA = "q&a"
    SUMMARIZATION = "summarization"
    MCQ = "mcq"


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    agent_type: Optional[AgentType] = Field(None, description="Specific agent to use (defaults to Q&A)")
    document_id: Optional[str] = Field(None, description="Document ID for context")
    mcq_count: Optional[int] = Field(None, description="Number of MCQ questions to generate (defaults to 5)")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[], description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Agent response")
    agent_type: AgentType = Field(..., description="Agent that generated the response")
    sources: Optional[List[Dict[str, Any]]] = Field(
        default=[], description="Source documents or data used"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional metadata"
    )


class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Document type")
    status: str = Field(..., description="Processing status")
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Document metadata"
    )


class MCQQuestion(BaseModel):
    """MCQ question model."""
    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., description="Answer options")
    correct_answer: int = Field(..., description="Index of correct answer")
    rationale: str = Field(..., description="Explanation for the correct answer")


class MCQResponse(BaseModel):
    """MCQ generation response model."""
    questions: List[MCQQuestion] = Field(..., description="Generated questions")
    document_id: str = Field(..., description="Source document ID")
    topic: str = Field(..., description="Question topic")


class SummaryResponse(BaseModel):
    """Summary response model."""
    executive_summary: str = Field(..., description="Executive summary")
    key_quotes: List[Dict[str, str]] = Field(
        ..., description="Key quotes with citations"
    )
    document_id: str = Field(..., description="Source document ID")
    word_count: int = Field(..., description="Original document word count")


class AnalyticsResponse(BaseModel):
    """Analytics response model."""
    kpis: Dict[str, Any] = Field(..., description="Key Performance Indicators")
    trends: List[Dict[str, Any]] = Field(..., description="Trend analysis")
    anomalies: List[Dict[str, Any]] = Field(..., description="Anomaly detection")
    insights: List[str] = Field(..., description="Business insights")
    document_id: str = Field(..., description="Source document ID")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")

