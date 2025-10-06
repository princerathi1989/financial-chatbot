"""Enhanced API layer for document-based financial chatbot."""

from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, AgentType, DocumentUploadResponse
from app.workflow.financial_workflow import FinancialWorkflow, FinancialRequest
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.storage.vector_store import vector_store

class EnhancedFinancialChatbot:
    """Enhanced chatbot focused on user-uploaded documents."""
    
    def __init__(self):
        self.workflow = FinancialWorkflow()
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.vector_store = vector_store
        self.logger = logger.bind(component="enhanced_chatbot")
    
    def process_chat_message(self, request: ChatRequest, document_id: Optional[str] = None) -> ChatResponse:
        """Process a chat message using uploaded documents."""
        try:
            # Search uploaded documents if document_id is provided
            context = ""
            if document_id:
                search_results = self.vector_store.search_similar_chunks(
                    query=request.message,
                    document_id=document_id,
                    top_k=5
                )
                context = self._prepare_context_from_search_results(search_results)
            
            # Convert to workflow request
            workflow_request = FinancialRequest(
                message=request.message,
                document_id=document_id,
                agent_type=request.agent_type.value if request.agent_type else None,
                context=context
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
                    'document_id': document_id,
                    'context_used': bool(context)
                }
            )
            
            self.logger.info(f"Processed message with {response.agent_type} agent using document {document_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again.",
                agent_type=AgentType.RAG,
                sources=[],
                metadata={"error": str(e)}
            )
    
    def _prepare_context_from_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context string from search results."""
        if not search_results:
            return ""
        
        context_parts = ["=== RELEVANT DOCUMENT CONTENT ==="]
        for result in search_results[:3]:  # Top 3 results
            context_parts.append(f"Content: {result['content'][:500]}...")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def upload_document(self, file_content: bytes, filename: str) -> DocumentUploadResponse:
        """Upload and process a document."""
        try:
            # Process the document
            metadata = self.ingestion_pipeline.process_document(file_content, filename)
            
            self.logger.info(f"Successfully uploaded document: {filename}")
            
            return DocumentUploadResponse(
                document_id=metadata['document_id'],
                filename=filename,
                document_type=metadata['file_type'],
                status='processed',
                metadata={
                    'total_chunks': metadata.get('total_chunks', 0),
                    'total_words': metadata.get('total_words', 0),
                    'file_size': len(file_content)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error uploading document: {e}")
            return DocumentUploadResponse(
                document_id="",
                filename=filename,
                document_type="unknown",
                status='error',
                metadata={"error": str(e)}
            )
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific document."""
        try:
            # Get document chunks to determine info
            chunks = self.vector_store.get_document_chunks(document_id)
            if not chunks:
                return None
            
            metadata = chunks[0]['metadata']
            
            return {
                'document_id': document_id,
                'filename': metadata.get('filename', 'Unknown'),
                'file_type': metadata.get('file_type', 'unknown'),
                'total_chunks': len(chunks),
                'upload_date': metadata.get('upload_date', 'Unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting document info: {e}")
            return None
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents."""
        try:
            # Get all document IDs from vector store
            # This is a simplified implementation - you might need to implement
            # a proper method in vector_store to get all document IDs
            documents = []
            
            # For now, return empty list - this would need proper implementation
            # based on your vector store's capabilities
            self.logger.info("Listed all documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            success = self.vector_store.delete_document(document_id)
            if success:
                self.logger.info(f"Successfully deleted document: {document_id}")
            else:
                self.logger.warning(f"Document not found: {document_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting document: {e}")
            return False
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search across all uploaded documents."""
        try:
            results = self.vector_store.search_similar_chunks(
                query=query,
                document_id=None,  # Search all documents
                top_k=top_k
            )
            
            self.logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        try:
            chunks = self.vector_store.get_document_chunks(document_id)
            self.logger.info(f"Retrieved {len(chunks)} chunks for document: {document_id}")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error getting document chunks: {e}")
            return []

# Global enhanced chatbot instance
enhanced_chatbot = EnhancedFinancialChatbot()