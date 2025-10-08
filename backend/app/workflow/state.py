"""LangGraph state management for financial chatbot workflow."""

from typing import Dict, List, Optional, Any, TypedDict
from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class FinancialState(TypedDict):
    """State for the financial chatbot workflow."""
    
    # Input
    message: str
    document_id: Optional[str]
    agent_type: Optional[str]
    
    # Processing
    context_chunks: List[Dict[str, Any]]
    document_content: Optional[str]
    
    # Output
    response: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    # Workflow control
    next_agent: Optional[str]
    error: Optional[str]
    completed: bool


class FinancialRequest(BaseModel):
    """Request model for financial workflow."""
    message: str
    document_id: Optional[str] = None
    agent_type: Optional[str] = None


class FinancialResponse(BaseModel):
    """Response model for financial workflow."""
    response: str
    agent_type: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
