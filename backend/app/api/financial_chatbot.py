"""Unified API layer for the Financial Multi-Agent Chatbot."""

from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, AgentType, DocumentUploadResponse
from app.workflow.financial_workflow import FinancialWorkflow, FinancialRequest
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.storage.vector_store import get_vector_store
from dotenv import load_dotenv

load_dotenv()


class FinancialChatbot:
    """Unified chatbot for financial document processing and Q&A."""
    
    def __init__(self):
        self.workflow = FinancialWorkflow()
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.document_store = {}  # In production, this would be a proper database
        self.logger = logger.bind(component="financial_chatbot")
    
    def process_chat_message(self, request: ChatRequest, document_id: Optional[str] = None) -> ChatResponse:
        """Process a chat message using LangGraph workflow with optional document context."""
        try:
            # Prepare context from document if provided
            context = ""
            if document_id:
                vector_store = get_vector_store()
                search_results = vector_store.search_similar_chunks(
                    query=request.message,
                    document_id=document_id,
                    top_k=settings.rag_top_k_results
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
                agent_type=AgentType.QnA,
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
            
            # Store document metadata
            document_id = metadata['document_id']
            self.document_store[document_id] = metadata
            
            # Add to vector store if it has chunks
            if 'chunks' in metadata and metadata['chunks']:
                self.logger.info(f"🔄 UPLOAD: Adding document {document_id} ({filename}) to vector store...")
                vector_store = get_vector_store()
                vector_store.add_document_chunks(
                    document_id=document_id,
                    chunks=metadata['chunks'],
                    metadata={
                        'filename': metadata['filename'],
                        'file_type': metadata['file_type'],
                        'total_chunks': metadata['total_chunks']
                    }
                )
                self.logger.info(f"🎉 UPLOAD COMPLETE: Document {document_id} ({filename}) successfully processed and stored!")
            else:
                self.logger.warning(f"⚠️ UPLOAD WARNING: Document {document_id} ({filename}) has no chunks to store")
            
            return DocumentUploadResponse(
                document_id=document_id,
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
                document_type="pdf",  # Default to pdf since we only support PDFs
                status='error',
                metadata={"error": str(e)}
            )
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific document."""
        try:
            # First check local document store
            if document_id in self.document_store:
                doc_data = self.document_store[document_id]
                return {
                    'document_id': document_id,
                    'filename': doc_data['filename'],
                    'file_type': doc_data['file_type'],
                    'total_chunks': doc_data.get('total_chunks', 0),
                    'total_words': doc_data.get('total_words', 0),
                    'status': doc_data.get('status', 'processed')
                }
            
            # Fallback to vector store
            vector_store = get_vector_store()
            chunks = vector_store.get_document_chunks(document_id)
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
            # Get documents from local store first
            documents = []
            for doc_id, doc_data in self.document_store.items():
                documents.append({
                    'document_id': doc_id,
                    'filename': doc_data['filename'],
                    'file_type': doc_data['file_type'],
                    'status': doc_data.get('status', 'processed'),
                    'total_chunks': doc_data.get('total_chunks', 0)
                })
            
            self.logger.info(f"Listed {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated data."""
        try:
            success = False
            
            # Remove from vector store
            vector_store = get_vector_store()
            vector_success = vector_store.delete_document(document_id)
            
            # Remove from document store
            if document_id in self.document_store:
                del self.document_store[document_id]
                success = True
            
            if vector_success or success:
                self.logger.info(f"Successfully deleted document {document_id}")
                return True
            else:
                self.logger.warning(f"Document {document_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search across all uploaded documents."""
        try:
            vector_store = get_vector_store()
            results = vector_store.search_similar_chunks(
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
            vector_store = get_vector_store()
            chunks = vector_store.get_document_chunks(document_id)
            self.logger.info(f"Retrieved {len(chunks)} chunks for document: {document_id}")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error getting document chunks: {e}")
            return []


# Global chatbot instance
chatbot = FinancialChatbot()
