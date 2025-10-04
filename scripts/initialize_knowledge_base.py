#!/usr/bin/env python3
"""
Knowledge Base Initialization Script
Initializes the permanent financial knowledge base with curated financial documents.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from storage.permanent_knowledge_base import permanent_knowledge_base
from scripts.financial_document_collector import FinancialDocumentCollector

def initialize_knowledge_base():
    """Initialize the permanent financial knowledge base."""
    try:
        logger.info("Starting knowledge base initialization...")
        
        # Check if knowledge base already exists
        stats = permanent_knowledge_base.get_knowledge_base_stats()
        if stats['total_documents'] > 0:
            logger.info(f"Knowledge base already initialized with {stats['total_documents']} documents")
            logger.info(f"Available domains: {', '.join(stats['domains'])}")
            
            response = input("Do you want to reinitialize? This will clear existing data. (y/N): ")
            if response.lower() != 'y':
                logger.info("Initialization cancelled")
                return
        
        # Initialize with sample documents
        logger.info("Collecting financial documents...")
        collector = FinancialDocumentCollector()
        documents = collector.collect_sample_documents()
        
        logger.info(f"Collected {len(documents)} financial documents")
        
        # Save documents to filesystem
        saved_paths = collector.save_documents(documents)
        logger.info(f"Saved {len(saved_paths)} documents to filesystem")
        
        # The permanent knowledge base will automatically initialize when imported
        # This happens in the __init__ method of PermanentKnowledgeBase
        
        # Get final stats
        final_stats = permanent_knowledge_base.get_knowledge_base_stats()
        
        logger.info("Knowledge base initialization completed successfully!")
        logger.info(f"Total documents: {final_stats['total_documents']}")
        logger.info(f"Total chunks: {final_stats['total_chunks']}")
        logger.info(f"Available domains: {', '.join(final_stats['domains'])}")
        
        # Print domain-wise counts
        logger.info("Domain-wise document counts:")
        for domain, count in final_stats['domain_counts'].items():
            logger.info(f"  - {domain}: {count} documents")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {e}")
        return False

def main():
    """Main function."""
    print("🤖 Financial Multi-Agent Chatbot - Knowledge Base Initialization")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not (project_root / "storage").exists():
        logger.error("Please run this script from the project root directory")
        sys.exit(1)
    
    # Initialize knowledge base
    success = initialize_knowledge_base()
    
    if success:
        print("\n✅ Knowledge base initialization completed successfully!")
        print("\nYou can now:")
        print("1. Start the chatbot: python main_enhanced.py")
        print("2. Test the API: curl http://localhost:8000/knowledge-base/stats")
        print("3. View available domains: curl http://localhost:8000/knowledge-base/domains")
    else:
        print("\n❌ Knowledge base initialization failed!")
        print("Please check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

