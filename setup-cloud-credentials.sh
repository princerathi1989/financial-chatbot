#!/bin/bash
# Setup script for Pinecone cloud service credentials
# This script helps you configure Pinecone for vector indexing

echo "🚀 Financial Multi-Agent Chatbot - Pinecone Setup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "📋 Required Cloud Services Setup:"
echo "1. Pinecone (Vector Store) - FREE tier available"
echo "2. OpenAI (AI API) - Pay per use"
echo ""

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local is_secret="$3"
    
    echo -n "$prompt: "
    if [ "$is_secret" = "true" ]; then
        read -s value
        echo ""
    else
        read value
    fi
    
    if [ -n "$value" ]; then
        export "$var_name"="$value"
        print_status "$var_name set"
    else
        print_error "$var_name not provided"
        return 1
    fi
}

# OpenAI API Key (Required)
echo "🤖 OpenAI Setup (Required)"
echo "-------------------------"
echo "1. Go to: https://platform.openai.com"
echo "2. Sign up and verify email/phone"
echo "3. Go to API Keys → Create new secret key"
echo "4. Copy the API key (starts with sk-)"
echo ""
prompt_input "Enter your OpenAI API key" "OPENAI_API_KEY" "true"

# Pinecone Setup
echo ""
echo "🔍 Pinecone Setup (Vector Store)"
echo "-------------------------------"
echo "1. Go to: https://www.pinecone.io"
echo "2. Sign up and verify email"
echo "3. Go to API Keys → Create new API key"
echo "4. Copy the API key"
echo ""
prompt_input "Enter your Pinecone API key" "PINECONE_API_KEY" "true"

# Optional: LangSmith Setup
echo ""
echo "📊 LangSmith Setup (Optional - FREE tier)"
echo "----------------------------------------"
echo "1. Go to: https://smith.langchain.com"
echo "2. Sign up and verify email"
echo "3. Go to Settings → API Keys"
echo "4. Create new API key"
echo ""
read -p "Do you want to set up LangSmith? (y/n): " setup_langsmith
if [ "$setup_langsmith" = "y" ] || [ "$setup_langsmith" = "Y" ]; then
    prompt_input "Enter your LangSmith API key" "LANGSMITH_API_KEY" "true"
fi

# Create environment file
echo ""
echo "🔧 Creating environment file..."
cat > .env << EOF
# Financial Multi-Agent Chatbot Configuration
# Session-based processing with Pinecone vector store

# OpenAI Configuration (Required)
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# LangSmith Configuration (Optional - FREE TIER)
LANGSMITH_API_KEY=${LANGSMITH_API_KEY:-}
LANGSMITH_PROJECT=financial-chatbot
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
API_HOST=0.0.0.0
API_PORT=8000

# Vector Store - Pinecone (FREE tier + Pay-as-you-go)
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=${PINECONE_API_KEY}
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=financial-documents
PINECONE_METRIC=cosine

# Database Configuration (in-memory only for session-based processing)
DATABASE_TYPE=memory

# Agent Configuration
RAG_TOP_K_RESULTS=5
SUMMARY_MAX_LENGTH=500
MCQ_NUM_QUESTIONS=5
ANALYTICS_CONFIDENCE_THRESHOLD=0.8

# Document Processing Settings
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF

print_status "Environment file created: .env"

print_status "Setup Complete!"
echo ""
echo "💰 Monthly Cost Breakdown:"
echo "   • Pinecone: FREE tier + usage-based pricing"
echo "   • OpenAI API: Pay per use (~$5-15/month)"
echo "   • Total: ~$5-15/month"
echo ""
echo "🚀 Next steps:"
echo "   1. Start the application: python main.py"
echo "   2. Access your chatbot: http://localhost:8000/docs"
echo "   3. Upload documents and start chatting!"
echo ""
echo "📝 Note: Documents are processed in-memory and not permanently stored."
echo "   Only vector embeddings are stored in Pinecone for similarity search."
