"""Document ingestion pipeline for PDFs and CSVs."""

import os
import uuid
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from loguru import logger
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
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or settings.max_chunk_size
        overlap = overlap or settings.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
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


class CSVProcessor(DocumentProcessor):
    """Enhanced CSV document processor with improved chunking strategies."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.csv']
        self.chunk_size = settings.max_chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CSV data for insights."""
        analysis = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'date_columns': []
        }
        
        # Detect date columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].dropna().iloc[0])
                    analysis['date_columns'].append(col)
                except:
                    pass
        
        return analysis
    
    def create_structured_chunks(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Create structured chunks from CSV data with multiple strategies."""
        chunks = []
        
        # Strategy 1: Document Overview Chunk
        overview_chunk = self._create_overview_chunk(df, analysis)
        chunks.append(overview_chunk)
        
        # Strategy 2: Column Analysis Chunks
        column_chunks = self._create_column_analysis_chunks(df, analysis)
        chunks.extend(column_chunks)
        
        # Strategy 3: Statistical Summary Chunks
        stats_chunks = self._create_statistical_chunks(df, analysis)
        chunks.extend(stats_chunks)
        
        # Strategy 4: Row-based Chunks (for detailed data access)
        row_chunks = self._create_row_based_chunks(df)
        chunks.extend(row_chunks)
        
        # Strategy 5: Category-based Chunks (for categorical data)
        category_chunks = self._create_category_chunks(df, analysis)
        chunks.extend(category_chunks)
        
        # Strategy 6: Time-series Chunks (if date columns exist)
        if analysis['date_columns']:
            timeseries_chunks = self._create_timeseries_chunks(df, analysis)
            chunks.extend(timeseries_chunks)
        
        return chunks
    
    def _create_overview_chunk(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> str:
        """Create comprehensive overview chunk."""
        overview = f"""CSV Document Overview:
Dataset: {df.shape[0]} rows × {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}
Numeric columns: {', '.join(analysis['numeric_columns']) if analysis['numeric_columns'] else 'None'}
Categorical columns: {', '.join(analysis['categorical_columns']) if analysis['categorical_columns'] else 'None'}
Date columns: {', '.join(analysis['date_columns']) if analysis['date_columns'] else 'None'}

Data Types:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}"""
        return overview
    
    def _create_column_analysis_chunks(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Create detailed analysis chunks for each column."""
        chunks = []
        
        for col in df.columns:
            col_chunk = f"Column Analysis: {col}\n"
            col_chunk += f"Data Type: {df[col].dtype}\n"
            col_chunk += f"Missing Values: {df[col].isnull().sum()}\n"
            
            if col in analysis['numeric_columns']:
                stats = df[col].describe()
                col_chunk += f"""Statistical Summary:
Count: {stats['count']:.0f}
Mean: {stats['mean']:.2f}
Std: {stats['std']:.2f}
Min: {stats['min']:.2f}
25%: {stats['25%']:.2f}
50%: {stats['50%']:.2f}
75%: {stats['75%']:.2f}
Max: {stats['max']:.2f}"""
            else:
                unique_count = df[col].nunique()
                col_chunk += f"Unique Values: {unique_count}\n"
                if unique_count <= 20:  # Show all values if not too many
                    unique_vals = df[col].value_counts().head(10)
                    col_chunk += f"Top Values:\n{unique_vals.to_string()}"
                else:
                    top_vals = df[col].value_counts().head(5)
                    col_chunk += f"Top 5 Values:\n{top_vals.to_string()}"
            
            chunks.append(col_chunk)
        
        return chunks
    
    def _create_statistical_chunks(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Create statistical analysis chunks."""
        chunks = []
        
        if analysis['numeric_columns']:
            # Correlation analysis
            numeric_df = df[analysis['numeric_columns']]
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                corr_chunk = f"Correlation Matrix:\n{corr_matrix.to_string()}"
                chunks.append(corr_chunk)
            
            # Summary statistics
            summary_stats = df[analysis['numeric_columns']].describe()
            stats_chunk = f"Summary Statistics:\n{summary_stats.to_string()}"
            chunks.append(stats_chunk)
        
        return chunks
    
    def _create_row_based_chunks(self, df: pd.DataFrame) -> List[str]:
        """Create chunks based on rows for detailed data access."""
        chunks = []
        rows_per_chunk = max(1, self.chunk_size // (len(df.columns) * 20))  # Estimate rows per chunk
        
        for start_idx in range(0, len(df), rows_per_chunk):
            end_idx = min(start_idx + rows_per_chunk, len(df))
            chunk_df = df.iloc[start_idx:end_idx]
            
            chunk_text = f"Data Rows {start_idx + 1}-{end_idx}:\n"
            chunk_text += chunk_df.to_string(index=False)
            chunks.append(chunk_text)
        
        return chunks
    
    def _create_category_chunks(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Create chunks for categorical data analysis."""
        chunks = []
        
        for col in analysis['categorical_columns']:
            if df[col].nunique() <= 50:
                value_counts = df[col].value_counts()
                category_chunk = f"Category Analysis for {col}:\n{value_counts.to_string()}"
                chunks.append(category_chunk)
        
        return chunks
    
    def _create_timeseries_chunks(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Create time-series analysis chunks."""
        chunks = []
        
        for date_col in analysis['date_columns']:
            try:
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col])
                
                # Time range analysis
                time_range = f"Time Series Analysis for {date_col}:\n"
                time_range += f"Date Range: {df_temp[date_col].min()} to {df_temp[date_col].max()}\n"
                time_range += f"Total Days: {(df_temp[date_col].max() - df_temp[date_col].min()).days}\n"
                
                # Monthly/yearly aggregations if numeric columns exist
                if analysis['numeric_columns']:
                    numeric_cols = [col for col in analysis['numeric_columns'] if col != date_col]
                    if numeric_cols:
                        monthly_agg = df_temp.groupby(df_temp[date_col].dt.to_period('M'))[numeric_cols].sum()
                        time_range += f"Monthly Aggregation:\n{monthly_agg.to_string()}"
                
                chunks.append(time_range)
            except Exception as e:
                logger.warning(f"Error creating timeseries chunk for {date_col}: {e}")
        
        return chunks
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process CSV document with enhanced chunking strategies."""
        try:
            df = pd.read_csv(file_path)
            analysis = self.analyze_data(df)
            
            chunks = self.create_structured_chunks(df, analysis)
            
            # Add metadata to each chunk
            enhanced_chunks = []
            for i, chunk in enumerate(chunks):
                enhanced_chunk = f"[CSV_CHUNK_{i+1}]\n{chunk}"
                enhanced_chunks.append(enhanced_chunk)
            
            metadata = {
                'dataframe': df,
                'analysis': analysis,
                'sample_data': df.head(10).to_dict('records'),
                'summary_stats': df.describe().to_dict() if analysis['numeric_columns'] else {},
                'chunks': enhanced_chunks,
                'total_chunks': len(enhanced_chunks),
                'total_words': sum(len(chunk.split()) for chunk in enhanced_chunks),
                'chunking_strategy': 'multi_strategy_csv'
            }
            
            logger.info(f"Processed CSV: {df.shape[0]} rows, {df.shape[1]} columns, {len(enhanced_chunks)} chunks using multi-strategy approach")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing CSV {file_path}: {e}")
            raise


class DocumentIngestionPipeline:
    """Main document ingestion pipeline."""
    
    def __init__(self):
        self.processors = {
            'pdf': PDFProcessor(),
            'csv': CSVProcessor()
        }
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type from extension."""
        ext = Path(filename).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext == '.csv':
            return 'csv'
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
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
            # Save file
            file_path, document_id = self.save_file(file_content, filename)
            
            # Determine file type
            file_type = self.get_file_type(filename)
            
            # Process document
            processor = self.processors[file_type]
            metadata = processor.process(file_path)
            
            # Add document metadata
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
        # In a production system, this would query a database
        # For now, we'll implement a simple file-based lookup
        try:
            # This is a simplified implementation
            # In production, you'd store metadata in a database
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None

