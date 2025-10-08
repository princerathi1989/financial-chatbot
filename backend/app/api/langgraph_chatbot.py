"""Simplified API layer using LangGraph workflow."""

from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, AgentType, DocumentUploadResponse
from app.workflow.financial_workflow import FinancialWorkflow, FinancialRequest
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.storage.vector_store import get_vector_store
from dotenv import load_dotenv

load_dotenv()  

class LangGraphChatbot:
    """Simplified chatbot using LangGraph workflow."""
    
    def __init__(self):
        self.workflow = FinancialWorkflow()
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.document_store = {}  # In production, this would be a proper database
        self.logger = logger.bind(component="langgraph_chatbot")
    
    def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message using LangGraph workflow."""
        try:
            # Convert to workflow request
            workflow_request = FinancialRequest(
                message=request.message,
                document_id=request.document_id,
                agent_type=request.agent_type.value if request.agent_type else None
            )
            
            # Execute workflow
            workflow_response = self.workflow.process_request(workflow_request)
            
            # Convert to API response
            response = ChatResponse(
                response=workflow_response.response,
                agent_type=AgentType(workflow_response.agent_type),
                sources=workflow_response.sources,
                metadata=workflow_response.metadata
            )
            
            self.logger.info(f"Processed message with {response.agent_type} agent")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again.",
                agent_type=AgentType.RAG,
                sources=[],
                metadata={"error": str(e)}
            )
    
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
                vector_store = get_vector_store()  # Get the initialized vector store
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
        return self.document_store.get(document_id)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents."""
        return [
            {
                'document_id': doc_id,
                'filename': doc_data['filename'],
                'file_type': doc_data['file_type'],
                'status': doc_data['status']
            }
            for doc_id, doc_data in self.document_store.items()
        ]
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated data."""
        try:
            if document_id in self.document_store:
                # Remove from vector store
                vector_store = get_vector_store()
                vector_store.delete_document(document_id)
                
                # Remove from document store
                del self.document_store[document_id]
                
                self.logger.info(f"Successfully deleted document {document_id}")
                return True
            else:
                self.logger.warning(f"Document {document_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting document {document_id}: {e}")
            return False


# Global chatbot instance
chatbot = LangGraphChatbot()
