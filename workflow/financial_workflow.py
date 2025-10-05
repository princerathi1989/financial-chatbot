"""LangGraph workflow implementation for financial multi-agent chatbot."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from loguru import logger

from .state import FinancialState, FinancialRequest, FinancialResponse
from core.config import settings
from storage.vector_store import vector_store


class FinancialWorkflow:
    """LangGraph-based workflow for financial multi-agent chatbot."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.1,
            max_tokens=2000
        )
        self.logger = logger.bind(component="financial_workflow")
        self.graph = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(FinancialState)
        
        # Add nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("rag_agent", self._rag_agent_node)
        workflow.add_node("summarization_agent", self._summarization_agent_node)
        workflow.add_node("mcq_agent", self._mcq_agent_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "rag": "rag_agent",
                "summarization": "summarization_agent", 
                "mcq": "mcq_agent",
                "error": "error_handler"
            }
        )
        
        # All agents end the workflow
        workflow.add_edge("rag_agent", END)
        workflow.add_edge("summarization_agent", END)
        workflow.add_edge("mcq_agent", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    @traceable(name="financial_router")
    def _router_node(self, state: FinancialState) -> FinancialState:
        """Route the request to the appropriate agent."""
        try:
            message = state["message"].lower()
            
            # Determine agent type based on keywords
            if any(keyword in message for keyword in ["summarize", "summary", "executive summary", "key points"]):
                agent_type = "summarization"
            elif any(keyword in message for keyword in ["quiz", "test", "questions", "mcq", "multiple choice"]):
                agent_type = "mcq"
            else:
                # Default to RAG for all other queries (including analytics queries)
                agent_type = "rag"
            
            # Override with explicit agent type if provided
            if state.get("agent_type"):
                agent_type = state["agent_type"]
            
            state["next_agent"] = agent_type
            self.logger.info(f"Routed to {agent_type} agent")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in router: {e}")
            state["error"] = str(e)
            state["next_agent"] = "error"
            return state
    
    def _route_decision(self, state: FinancialState) -> str:
        """Decision function for routing."""
        if state.get("error"):
            return "error"
        return state.get("next_agent", "rag")
    
    @traceable(name="financial_rag_agent")
    def _rag_agent_node(self, state: FinancialState) -> FinancialState:
        """Enhanced RAG agent node for question answering and analytics."""
        try:
            query = state["message"]
            document_id = state.get("document_id")
            
            # Check if this is an analytics query
            is_analytics_query = self._is_analytics_query(query)
            
            # Retrieve relevant context
            context_chunks = vector_store.search_similar_chunks(
                query=query,
                top_k=settings.rag_top_k_results,
                document_id=document_id
            )
            
            if not context_chunks:
                state["response"] = "I couldn't find relevant financial information in the uploaded documents to answer your question."
                state["sources"] = []
                state["metadata"] = {"context_chunks_found": 0}
                return state
            
            # Generate answer using LangChain with analytics awareness
            context_text = "\n\n".join([
                f"Source {i+1} (Document: {chunk.get('metadata', {}).get('filename', 'Unknown')}):\n{chunk['content']}" 
                for i, chunk in enumerate(context_chunks)
            ])
            
            # Determine document types in context
            document_types = set()
            for chunk in context_chunks:
                doc_type = chunk.get('metadata', {}).get('file_type', 'unknown')
                document_types.add(doc_type)
            
            # Create analytics-aware prompt
            if is_analytics_query and 'csv' in document_types:
                prompt = self._create_analytics_prompt()
            else:
                prompt = self._create_standard_prompt()
            
            chain = prompt | self.llm
            response = chain.invoke({
                "context": context_text,
                "question": query,
                "document_types": ", ".join(document_types)
            })
            
            # Prepare sources
            sources = []
            for chunk in context_chunks:
                sources.append({
                    "content": chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                    "metadata": chunk['metadata'],
                    "relevance_score": 1 - chunk.get('distance', 0),
                    "document_type": chunk.get('metadata', {}).get('file_type', 'unknown')
                })
            
            state["response"] = response.content.strip()
            state["sources"] = sources
            state["metadata"] = {
                "context_chunks_found": len(context_chunks),
                "document_id": document_id,
                "agent_type": "rag",
                "is_analytics_query": is_analytics_query,
                "document_types": list(document_types)
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in RAG agent: {e}")
            state["error"] = str(e)
            state["response"] = "I encountered an error while processing your financial question. Please try again."
            return state
    
    def _is_analytics_query(self, query: str) -> bool:
        """Determine if the query requires analytics processing."""
        analytics_keywords = [
            "kpi", "trends", "analytics", "insights", "anomalies", "analysis",
            "calculate", "computation", "statistics", "metrics", "performance",
            "revenue", "profit", "margin", "growth", "decline", "correlation",
            "pattern", "forecast", "prediction", "comparison", "ratio"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in analytics_keywords)
    
    def _create_analytics_prompt(self) -> ChatPromptTemplate:
        """Create prompt for analytics queries."""
        return ChatPromptTemplate.from_template("""
You are a senior financial analyst and expert assistant specializing in financial document analysis, Q&A, and data analytics.

Context from financial documents (including CSV data):
{context}

Question: {question}

Instructions for Analytics Queries:
- Analyze the financial data and provide comprehensive insights
- Calculate relevant KPIs, ratios, and metrics when possible
- Identify trends, patterns, and anomalies in the data
- Provide quantitative analysis with specific numbers and percentages
- Compare different time periods or categories when relevant
- Highlight key business insights and recommendations
- Use proper financial terminology and maintain professional tone
- If CSV data is present, perform statistical analysis and calculations
- Cite specific data points and sources in your analysis

Document Types Available: {document_types}

Answer with detailed analytics:
""")
    
    def _create_standard_prompt(self) -> ChatPromptTemplate:
        """Create prompt for standard Q&A queries."""
        return ChatPromptTemplate.from_template("""
You are a senior financial analyst and expert assistant specializing in financial document analysis and Q&A.

Context from financial documents:
{context}

Question: {question}

Instructions:
- Provide a comprehensive and accurate answer based on the financial context provided
- If the context doesn't contain enough information, clearly state this limitation
- Cite specific information from the sources when possible
- Be precise and professional in your response
- Focus on financial insights, metrics, and analysis
- Use proper financial terminology and maintain professional tone
- Handle both PDF and CSV data appropriately

Answer:
""")
    
    @traceable(name="financial_summarization_agent")
    def _summarization_agent_node(self, state: FinancialState) -> FinancialState:
        """Summarization agent node."""
        try:
            document_id = state.get("document_id")
            
            if not document_id:
                state["response"] = "Please specify a document ID to generate a summary."
                state["sources"] = []
                state["metadata"] = {}
                return state
            
            # Get document chunks
            chunks = vector_store.get_document_chunks(document_id)
            
            if not chunks:
                state["response"] = "No document content found for summarization."
                state["sources"] = []
                state["metadata"] = {}
                return state
            
            # Combine chunks for summarization
            full_text = "\n\n".join([chunk['content'] for chunk in chunks])
            
            prompt = ChatPromptTemplate.from_template("""
Create an executive summary of the following financial document:

Document content:
{document_content}

Instructions:
- Create a comprehensive executive summary (max 500 words)
- Extract 5-7 key financial quotes with context
- Focus on financial performance, risks, opportunities, and strategic insights
- Use professional financial language
- Highlight important metrics and trends

Format your response as:
EXECUTIVE SUMMARY:
[Your summary here]

KEY QUOTES:
1. "[Quote 1]" - [Context]
2. "[Quote 2]" - [Context]
[Continue for 5-7 quotes]
""")
            
            chain = prompt | self.llm
            response = chain.invoke({"document_content": full_text[:4000]})
            
            state["response"] = response.content.strip()
            state["sources"] = [{"type": "summary", "document_id": document_id}]
            state["metadata"] = {
                "agent_type": "summarization",
                "word_count": len(full_text.split())
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in summarization agent: {e}")
            state["error"] = str(e)
            state["response"] = "I encountered an error while generating the summary. Please try again."
            return state
    
    @traceable(name="financial_mcq_agent")
    def _mcq_agent_node(self, state: FinancialState) -> FinancialState:
        """MCQ generation agent node."""
        try:
            document_id = state.get("document_id")
            
            if not document_id:
                state["response"] = "Please specify a document ID to generate MCQ questions."
                state["sources"] = []
                state["metadata"] = {}
                return state
            
            # Get document chunks
            chunks = vector_store.get_document_chunks(document_id)
            
            if not chunks:
                state["response"] = "No document content found for MCQ generation."
                state["sources"] = []
                state["metadata"] = {}
                return state
            
            # Combine chunks for MCQ generation
            full_text = "\n\n".join([chunk['content'] for chunk in chunks])
            
            prompt = ChatPromptTemplate.from_template("""
Generate {num_questions} multiple choice questions based on the following financial document:

Document content:
{document_content}

Instructions:
- Create {num_questions} high-quality MCQ questions
- Focus on financial concepts, metrics, and analysis
- Each question should have 4 options (A, B, C, D)
- Provide the correct answer and rationale
- Questions should test understanding, not memorization
- Use professional financial terminology

Format your response as:
Q1: [Question text]
A. [Option A]
B. [Option B] 
C. [Option C]
D. [Option D]
Correct Answer: [Letter]
Rationale: [Explanation]

[Continue for all questions]
""")
            
            chain = prompt | self.llm
            response = chain.invoke({
                "document_content": full_text[:4000],
                "num_questions": settings.mcq_num_questions
            })
            
            state["response"] = response.content.strip()
            state["sources"] = [{"type": "mcq", "document_id": document_id}]
            state["metadata"] = {
                "agent_type": "mcq",
                "num_questions": settings.mcq_num_questions
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in MCQ agent: {e}")
            state["error"] = str(e)
            state["response"] = "I encountered an error while generating MCQ questions. Please try again."
            return state
    
    
    def _error_handler_node(self, state: FinancialState) -> FinancialState:
        """Error handler node."""
        error_msg = state.get("error", "Unknown error occurred")
        state["response"] = f"I encountered an error while processing your request: {error_msg}. Please try again."
        state["sources"] = []
        state["metadata"] = {"error": error_msg, "agent_type": "error"}
        return state
    
    @traceable(name="financial_workflow_execution")
    def process_request(self, request: FinancialRequest) -> FinancialResponse:
        """Process a financial request through the workflow."""
        try:
            # Initialize state
            initial_state: FinancialState = {
                "message": request.message,
                "document_id": request.document_id,
                "agent_type": request.agent_type,
                "context_chunks": [],
                "document_content": None,
                "csv_data": None,
                "response": "",
                "sources": [],
                "metadata": {},
                "next_agent": None,
                "error": None,
                "completed": False
            }
            
            # Execute workflow
            final_state = self.graph.invoke(initial_state)
            
            # Create response
            response = FinancialResponse(
                response=final_state["response"],
                agent_type=final_state["metadata"].get("agent_type", "rag"),
                sources=final_state["sources"],
                metadata=final_state["metadata"]
            )
            
            self.logger.info(f"Workflow completed successfully with {response.agent_type} agent")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in workflow execution: {e}")
            return FinancialResponse(
                response=f"I encountered an error while processing your request: {str(e)}. Please try again.",
                agent_type="error",
                sources=[],
                metadata={"error": str(e)}
            )
