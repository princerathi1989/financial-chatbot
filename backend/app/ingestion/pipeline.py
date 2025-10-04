"""Document ingestion pipeline for PDFs."""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings


class DocumentProcessor:
    """Base class for document processing."""
    
    def __init__(self):
        self.supported_extensions = []
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process a document and return metadata."""
        raise NotImplementedError


class PDFProcessor(DocumentProcessor):
    """PDF document processor."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.max_chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks using LangChain RecursiveCharacterTextSplitter."""
        try:
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks using RecursiveCharacterTextSplitter")
            return chunks
        except Exception as e:
            logger.error(f"Error chunking text with RecursiveCharacterTextSplitter: {e}")
            return self._fallback_chunk_text(text)
    
    def _fallback_chunk_text(self, text: str) -> List[str]:
        """Fallback chunking method if LangChain fails."""
        chunk_size = settings.max_chunk_size
        overlap = settings.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        logger.warning(f"Used fallback chunking: {len(chunks)} chunks")
        return chunks
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process PDF document."""
        try:
            text = self.extract_text(file_path)
            chunks = self.chunk_text(text)
            
            metadata = {
                'total_chunks': len(chunks),
                'total_characters': len(text),
                'total_words': len(text.split()),
                'chunks': chunks,
                'full_text': text
            }
            
            logger.info(f"Processed PDF: {len(chunks)} chunks, {len(text)} characters")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise




class DocumentIngestionPipeline:
    """Main document ingestion pipeline."""
    
    def __init__(self):
        self.processors = {
            'pdf': PDFProcessor()
        }
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type from extension."""
        ext = Path(filename).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        else:
            raise ValueError(f"Unsupported file type: {ext}. Only PDF files are supported.")
    
    def save_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to storage."""
        document_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        saved_filename = f"{document_id}{file_extension}"
        file_path = os.path.join(settings.upload_directory, saved_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path, document_id
    
    def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded document."""
        try:
            file_path, document_id = self.save_file(file_content, filename)
            
            file_type = self.get_file_type(filename)
            
            processor = self.processors[file_type]
            metadata = processor.process(file_path)
            
            metadata.update({
                'document_id': document_id,
                'filename': filename,
                'file_type': file_type,
                'file_path': file_path,
                'status': 'processed'
            })
            
            logger.info(f"Successfully processed document {document_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve processed document by ID."""
        try:
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None

