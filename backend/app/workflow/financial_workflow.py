"""LangGraph workflow implementation for financial multi-agent chatbot."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from loguru import logger

from .state import FinancialState, FinancialRequest, FinancialResponse
from app.core.config import settings
from app.storage.vector_store import get_vector_store


class FinancialWorkflow:
    """LangGraph-based workflow for financial multi-agent chatbot."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.1,
            max_tokens=500
        )
        self.logger = logger.bind(component="financial_workflow")
        self.graph = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(FinancialState)
        
        workflow.add_node("router", self._router_node)
        workflow.add_node("rag_agent", self._rag_agent_node)
        workflow.add_node("summarization_agent", self._summarization_agent_node)
        workflow.add_node("mcq_agent", self._mcq_agent_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "q&a": "rag_agent",
                "summarization": "summarization_agent", 
                "mcq": "mcq_agent",
                "error": "error_handler"
            }
        )
        
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
            
            if any(keyword in message for keyword in [
                "summarize", "summary", "executive summary", "key points", 
                "overview", "brief", "synopsis", "recap", "highlights"
            ]):
                agent_type = "summarization"
            elif any(keyword in message for keyword in [
                "quiz", "test", "questions", "mcq", "multiple choice",
                "examination", "assessment", "practice", "questions about"
            ]):
                agent_type = "mcq"
            else:
                agent_type = "q&a"
            
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
        return state.get("next_agent", "q&a")
    
    @traceable(name="financial_rag_agent")
    def _rag_agent_node(self, state: FinancialState) -> FinancialState:
        """Enhanced RAG agent node for question answering and analytics."""
        try:
            query = state["message"]
            document_id = state.get("document_id")
            
            is_analytics_query = self._is_analytics_query(query)
            query_complexity = self._get_query_complexity(query)
            
            vector_store = get_vector_store()
            context_chunks = vector_store.search_similar_chunks(
                query=query,
                top_k=settings.rag_top_k_results,
                document_id=None
            )
            
            if not context_chunks:
                state["response"] = "I couldn't find relevant financial information in the uploaded documents to answer your question."
                state["sources"] = []
                state["metadata"] = {"context_chunks_found": 0, "agent_type": "q&a"}
                return state
            
            context_text = "\n\n".join([
                f"Source {i+1} (Document: {chunk.get('metadata', {}).get('filename', 'Unknown')}):\n{chunk['content']}" 
                for i, chunk in enumerate(context_chunks)
            ])
            
            # Prepare conversation history for context
            conversation_context = ""
            conversation_history = state.get("conversation_history", [])
            converted_history = self._convert_conversation_history(conversation_history)
            if converted_history:
                conversation_context = "\n\nPrevious conversation:\n"
                for msg in converted_history[-5:]:  # Last 5 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_context += f"{role}: {msg['content']}\n"
            
            prompt = self._create_standard_prompt()
            
            chain = prompt | self.llm
            response = chain.invoke({
                "context": context_text + conversation_context,
                "question": query,
                "complexity": query_complexity
            })
            
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
                "agent_type": "q&a",
                "is_analytics_query": is_analytics_query,
                "query_complexity": query_complexity
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in RAG agent: {e}")
            state["error"] = str(e)
            state["response"] = "I encountered an error while processing your financial question. Please try again."
            state["metadata"] = {"agent_type": "q&a", "error": str(e)}
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
    
    def _convert_conversation_history(self, conversation_history):
        """Convert ChatMessage objects to dictionaries for processing."""
        if not conversation_history:
            return []
        
        converted = []
        for msg in conversation_history:
            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                # ChatMessage object
                converted.append({
                    'role': msg.role,
                    'content': msg.content
                })
            elif isinstance(msg, dict):
                # Already a dictionary
                converted.append(msg)
        return converted

    def _get_query_complexity(self, query: str) -> str:
        """Determine query complexity for dynamic response length."""
        query_lower = query.lower()
        
        simple_keywords = ["what is", "define", "explain briefly", "quick", "simple", "basic"]
        if any(keyword in query_lower for keyword in simple_keywords):
            return "simple"
        
        complex_keywords = [
            "comprehensive", "detailed", "thorough", "complete analysis", 
            "compare and contrast", "pros and cons", "advantages and disadvantages",
            "step by step", "how to", "process", "methodology", "strategy"
        ]
        if any(keyword in query_lower for keyword in complex_keywords):
            return "complex"
        
        return "moderate"
    
    
    def _create_standard_prompt(self) -> ChatPromptTemplate:
        """Create prompt for standard Q&A queries with dynamic length control."""
        return ChatPromptTemplate.from_template("""
You are a senior financial analyst and expert assistant specializing in financial document analysis and Q&A.

CRITICAL: Keep your response EXTREMELY SHORT - maximum 1-2 sentences or 1 short paragraph. Be direct and concise.

Context from financial documents:
{context}

Question: {question}

Instructions:
- Provide a concise and accurate answer based on the financial context provided
- If the context doesn't contain enough information, clearly state this limitation
- Cite specific information from the sources when possible
- Be precise and professional in your response
- Focus on financial insights, metrics, and analysis
- Use proper financial terminology and maintain professional tone
- Handle PDF data appropriately
- BE CONCISE: Focus on essential information only

Response Length Guidelines (Query Complexity: {complexity}):
- ALWAYS keep responses to 1-2 paragraphs maximum
- Be concise and direct - avoid unnecessary elaboration
- Focus on key information and actionable insights only
- Prioritize clarity and brevity over comprehensive detail
- Use bullet points when appropriate for better readability

Answer:
""")
    
    @traceable(name="financial_summarization_agent")
    def _summarization_agent_node(self, state: FinancialState) -> FinancialState:
        """Summarization agent node for multi-document summarization."""
        try:
            vector_store = get_vector_store()
            
            if vector_store.use_local_fallback:
                vector_store._load_local_data()
            
            chunks = vector_store.get_all_chunks()
            
            if not chunks:
                state["response"] = "No document content found for summarization. Please upload a document first."
                state["sources"] = []
                state["metadata"] = {"agent_type": "summarization"}
                return state
            
            full_text = "\n\n".join([chunk['content'] for chunk in chunks])
            
            # Prepare conversation history for context
            conversation_context = ""
            conversation_history = state.get("conversation_history", [])
            converted_history = self._convert_conversation_history(conversation_history)
            if converted_history:
                conversation_context = "\n\nPrevious conversation context:\n"
                for msg in converted_history[-3:]:  # Last 3 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_context += f"{role}: {msg['content']}\n"
            
            prompt = ChatPromptTemplate.from_template(f"""
Create an executive summary of the following financial document:

Document content:
{{document_content}}
{conversation_context}

Instructions:
- Create a comprehensive executive summary (max {settings.summary_max_length} words)
- Extract 5-7 key financial quotes with context
- Focus on financial performance, risks, opportunities, and strategic insights
- Use professional financial language
- Highlight important metrics and trends
- Consider any previous conversation context if relevant

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
            state["sources"] = [{"type": "summary", "document_id": "multi-document"}]
            state["metadata"] = {
                "agent_type": "summarization",
                "word_count": len(full_text.split())
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in summarization agent: {e}")
            state["error"] = str(e)
            state["response"] = "I encountered an error while generating the summary. Please try again."
            state["metadata"] = {"agent_type": "summarization", "error": str(e)}
            return state
    
    @traceable(name="financial_mcq_agent")
    def _mcq_agent_node(self, state: FinancialState) -> FinancialState:
        """MCQ generation agent node for multi-document content."""
        try:
            vector_store = get_vector_store()
            
            if vector_store.use_local_fallback:
                vector_store._load_local_data()
            
            chunks = vector_store.get_all_chunks()
            
            if not chunks:
                state["response"] = "No document content found for MCQ generation. Please upload a document first."
                state["sources"] = []
                state["metadata"] = {"agent_type": "mcq"}
                return state
            
            full_text = "\n\n".join([chunk['content'] for chunk in chunks])
            
            # Prepare conversation history for context
            conversation_context = ""
            conversation_history = state.get("conversation_history", [])
            converted_history = self._convert_conversation_history(conversation_history)
            if converted_history:
                conversation_context = "\n\nPrevious conversation context:\n"
                for msg in converted_history[-3:]:  # Last 3 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_context += f"{role}: {msg['content']}\n"
            
            prompt = ChatPromptTemplate.from_template("""
Generate {num_questions} multiple choice questions based on the following financial document:

Document content:
{document_content}
{conversation_context}

Instructions:
- Create {num_questions} high-quality MCQ questions
- Focus on financial concepts, metrics, and analysis
- Each question should have 4 options (A, B, C, D)
- Provide only the correct answer
- Questions should test understanding, not memorization
- Use professional financial terminology
- Consider any previous conversation context if relevant

Format your response as:
Q1: [Question text]
A. [Option A]
B. [Option B] 
C. [Option C]
D. [Option D]
Correct Answer: [Letter]

[Continue for all questions]
""")
            
            chain = prompt | self.llm
            response = chain.invoke({
                "document_content": full_text[:4000],
                "num_questions": settings.mcq_num_questions
            })
            
            state["response"] = response.content.strip()
            state["sources"] = [{"type": "mcq", "document_id": "multi-document"}]
            state["metadata"] = {
                "agent_type": "mcq",
                "num_questions": settings.mcq_num_questions
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error in MCQ agent: {e}")
            state["error"] = str(e)
            state["response"] = "I encountered an error while generating MCQ questions. Please try again."
            state["metadata"] = {"agent_type": "mcq", "error": str(e)}
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
            initial_state: FinancialState = {
                "message": request.message,
                "document_id": request.document_id,
                "agent_type": request.agent_type,
                "conversation_history": request.conversation_history,
                "context_chunks": [],
                "document_content": None,
                "response": "",
                "sources": [],
                "metadata": {},
                "next_agent": None,
                "error": None,
                "completed": False
            }
            
            final_state = self.graph.invoke(initial_state)
            
            response = FinancialResponse(
                response=final_state["response"],
                agent_type=final_state["metadata"].get("agent_type", "q&a"),
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
