"""Enhanced API layer with hybrid knowledge base integration."""

from typing import Dict, Any, Optional, List
from loguru import logger
from core.config import settings
from models.schemas import ChatRequest, ChatResponse, AgentType, DocumentUploadResponse
from workflow.financial_workflow import FinancialWorkflow, FinancialRequest
from ingestion.pipeline import DocumentIngestionPipeline
from storage.hybrid_knowledge_manager import hybrid_knowledge_manager

class EnhancedFinancialChatbot:
    """Enhanced chatbot with hybrid knowledge base (permanent + session)."""
    
    def __init__(self):
        self.workflow = FinancialWorkflow()
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.hybrid_kb = hybrid_knowledge_manager
        self.logger = logger.bind(component="enhanced_chatbot")
    
    def process_chat_message(self, request: ChatRequest, session_id: Optional[str] = None) -> ChatResponse:
        """Process a chat message using hybrid knowledge base."""
        try:
            # Search both permanent and session knowledge
            search_results = self.hybrid_kb.search_knowledge(
                query=request.message,
                session_id=session_id,
                top_k=10
            )
            
            # Prepare context from search results
            context = self._prepare_context_from_search_results(search_results)
            
            # Convert to workflow request with enhanced context
            workflow_request = FinancialRequest(
                message=request.message,
                document_id=request.document_id,
                agent_type=request.agent_type.value if request.agent_type else None,
                context=context  # Add context from knowledge base
            )
            
            # Execute workflow
            workflow_response = self.workflow.process_request(workflow_request)
            
            # Convert to API response
            response = ChatResponse(
                response=workflow_response.response,
                agent_type=AgentType(workflow_response.agent_type),
                sources=workflow_response.sources,
                metadata={
                    **workflow_response.metadata,
                    'knowledge_sources': {
                        'permanent_results': len(search_results['permanent_results']),
                        'session_results': len(search_results['session_results']),
                        'total_results': len(search_results['combined_results'])
                    }
                }
            )
            
            self.logger.info(f"Processed message with {response.agent_type} agent using hybrid knowledge")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again.",
                agent_type=AgentType.RAG,
                sources=[],
                metadata={"error": str(e)}
            )
    
    def _prepare_context_from_search_results(self, search_results: Dict[str, Any]) -> str:
        """Prepare context string from search results."""
        context_parts = []
        
        # Add permanent knowledge context
        if search_results['permanent_results']:
            context_parts.append("=== PERMANENT FINANCIAL KNOWLEDGE ===")
            for result in search_results['permanent_results'][:3]:  # Top 3 results
                context_parts.append(f"Source: {result['metadata'].get('title', 'Unknown')}")
                context_parts.append(f"Content: {result['content'][:500]}...")
                context_parts.append("")
        
        # Add session knowledge context
        if search_results['session_results']:
            context_parts.append("=== USER UPLOADED DOCUMENTS ===")
            for result in search_results['session_results'][:2]:  # Top 2 results
                context_parts.append(f"Source: {result['metadata'].get('filename', 'Unknown')}")
                context_parts.append(f"Content: {result['content'][:500]}...")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def create_session(self) -> str:
        """Create a new user session."""
        session_id = self.hybrid_kb.create_session()
        self.logger.info(f"Created new session: {session_id}")
        return session_id
    
    def upload_document_to_session(self, file_content: bytes, filename: str, session_id: str) -> DocumentUploadResponse:
        """Upload and process a document for a specific session."""
        try:
            # Process the document
            metadata = self.ingestion_pipeline.process_document(file_content, filename)
            
            # Add to session
            success = self.hybrid_kb.add_session_document(session_id, metadata)
            
            if success:
                self.logger.info(f"Successfully uploaded document to session {session_id}")
                
                return DocumentUploadResponse(
                    document_id=metadata['document_id'],
                    filename=filename,
                    document_type=metadata['file_type'],
                    status='processed',
                    metadata={
                        'total_chunks': metadata.get('total_chunks', 0),
                        'total_words': metadata.get('total_words', 0),
                        'file_size': len(file_content),
                        'session_id': session_id
                    }
                )
            else:
                raise Exception("Failed to add document to session")
            
        except Exception as e:
            self.logger.error(f"Error uploading document to session: {e}")
            return DocumentUploadResponse(
                document_id="",
                filename=filename,
                document_type="unknown",
                status='error',
                metadata={"error": str(e)}
            )
    
    def get_session_documents(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all documents in a session."""
        return self.hybrid_kb.get_session_documents(session_id)
    
    def remove_session_document(self, session_id: str, document_id: str) -> bool:
        """Remove a document from a session."""
        return self.hybrid_kb.remove_session_document(session_id, document_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session and all its documents."""
        return self.hybrid_kb.clear_session(session_id)
    
    def get_knowledge_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive knowledge statistics."""
        return self.hybrid_kb.get_knowledge_stats(session_id)
    
    def get_available_domains(self) -> List[str]:
        """Get list of available financial domains."""
        return self.hybrid_kb.get_available_domains()
    
    def search_domain_knowledge(self, domain: str, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Search knowledge for a specific domain."""
        return self.hybrid_kb.search_domain_knowledge(domain, query, session_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session information."""
        return self.hybrid_kb.get_session_info(session_id)
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session timeout."""
        return self.hybrid_kb.extend_session(session_id)
    
    # Legacy methods for backward compatibility
    def upload_document(self, file_content: bytes, filename: str) -> DocumentUploadResponse:
        """Legacy upload method - creates a temporary session."""
        session_id = self.create_session()
        return self.upload_document_to_session(file_content, filename, session_id)
    
    def get_document_info(self, document_id: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get information about a specific document."""
        if session_id:
            session_docs = self.get_session_documents(session_id)
            for doc in session_docs:
                if doc['document_id'] == document_id:
                    return doc
        return None
    
    def list_documents(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all documents (session or permanent)."""
        if session_id:
            return self.get_session_documents(session_id)
        else:
            # Return permanent knowledge base stats
            stats = self.get_knowledge_stats()
            return [
                {
                    'domain': domain,
                    'document_count': count,
                    'knowledge_type': 'permanent'
                }
                for domain, count in stats['permanent_knowledge']['domain_counts'].items()
            ]
    
    def delete_document(self, document_id: str, session_id: Optional[str] = None) -> bool:
        """Delete a document."""
        if session_id:
            return self.remove_session_document(session_id, document_id)
        else:
            # This would be for permanent documents (admin function)
            return self.hybrid_kb.remove_permanent_document(document_id)
    
    def add_custom_knowledge(self, title: str, content: str, domain: str, source: str = "custom") -> str:
        """Add custom knowledge to permanent knowledge base."""
        return self.hybrid_kb.add_custom_permanent_document(title, content, domain, source)
    
    def get_permanent_knowledge_domains(self) -> Dict[str, int]:
        """Get permanent knowledge domains with document counts."""
        stats = self.get_knowledge_stats()
        return stats['permanent_knowledge']['domain_counts']
    
    def cleanup_expired_sessions(self):
        """Manually trigger cleanup of expired sessions."""
        self.hybrid_kb.cleanup_expired_sessions()
        self.logger.info("Cleaned up expired sessions")

# Global enhanced chatbot instance
enhanced_chatbot = EnhancedFinancialChatbot()

