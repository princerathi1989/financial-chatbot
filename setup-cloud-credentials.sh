#!/bin/bash
# Setup script for cloud service credentials
# This script helps you configure all required environment variables

echo "🚀 Financial Multi-Agent Chatbot - Cloud Setup"
echo "=============================================="
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
echo "1. Zilliz Cloud Serverless (Vector Store) - FREE"
echo "2. Azure Blob Storage (File Storage) - FREE 5GB"
echo "3. MongoDB Atlas (Database) - FREE 512MB"
echo "4. OpenAI (AI API) - Pay per use"
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

# Zilliz Cloud Setup
echo ""
echo "🔍 Zilliz Cloud Setup (Vector Store)"
echo "------------------------------------"
echo "1. Go to: https://cloud.zilliz.com"
echo "2. Sign up and verify email"
echo "3. Go to Project Settings → API Keys"
echo "4. Create new API key (starts with zilliz-)"
echo ""
prompt_input "Enter your Zilliz API key" "ZILLIZ_API_KEY" "true"

# Azure Storage Setup
echo ""
echo "💾 Azure Blob Storage Setup (File Storage)"
echo "----------------------------------------"
echo "1. Go to: https://azure.microsoft.com/free/"
echo "2. Sign up (free account with $200 credit)"
echo "3. Create Storage Account in Azure Portal"
echo "4. Go to Access Keys and copy Storage Account Name and Key"
echo ""
prompt_input "Enter your Azure Storage Account name" "AZURE_STORAGE_ACCOUNT" "false"
prompt_input "Enter your Azure Storage Key" "AZURE_STORAGE_KEY" "true"

# MongoDB Atlas Setup
echo ""
echo "🗄️ MongoDB Atlas Setup (Database)"
echo "--------------------------------"
echo "1. Go to: https://cloud.mongodb.com"
echo "2. Sign up and verify email"
echo "3. Create M0 Sandbox cluster (FREE)"
echo "4. Create database user"
echo "5. Whitelist IP address (0.0.0.0/0)"
echo "6. Get connection string from Connect → Connect your application"
echo ""
prompt_input "Enter your MongoDB connection string" "MONGODB_CONNECTION_STRING" "true"

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
# Ultra-Budget Setup (~$7-17/month)

# OpenAI Configuration (Required)
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_MODEL=gpt-4-turbo-preview

# LangSmith Configuration (Optional - FREE TIER)
LANGSMITH_API_KEY=${LANGSMITH_API_KEY:-}
LANGSMITH_PROJECT=financial-chatbot-budget

# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50

# Vector Store - Zilliz Cloud Serverless (FREE TIER + Pay-as-you-go)
VECTOR_STORE_TYPE=zilliz
ZILLIZ_API_KEY=${ZILLIZ_API_KEY}
ZILLIZ_CLOUD_REGION=us-east-1
ZILLIZ_COLLECTION_NAME=financial_documents

# Storage - Azure Blob Storage (FREE TIER: 5GB)
STORAGE_TYPE=azure
AZURE_STORAGE_ACCOUNT=${AZURE_STORAGE_ACCOUNT}
AZURE_STORAGE_KEY=${AZURE_STORAGE_KEY}
AZURE_CONTAINER_NAME=financial-documents

# Database - MongoDB Atlas (FREE TIER: 512MB)
DATABASE_TYPE=mongodb
MONGODB_CONNECTION_STRING=${MONGODB_CONNECTION_STRING}
MONGODB_DATABASE_NAME=financial_chatbot

# Agent Configuration
RAG_TOP_K_RESULTS=5
SUMMARY_MAX_LENGTH=500
MCQ_NUM_QUESTIONS=5
ANALYTICS_CONFIDENCE_THRESHOLD=0.8
EOF

print_status "Environment file created: .env"

# Test configuration
echo ""
echo "🧪 Testing configuration..."
python test_cheapest_config.py

if [ $? -eq 0 ]; then
    print_status "Configuration test passed!"
    echo ""
    echo "🎉 Setup Complete!"
    echo ""
    echo "💰 Monthly Cost Breakdown:"
    echo "   • Zilliz Cloud Serverless: FREE (with usage-based pricing)"
    echo "   • Azure Blob Storage: FREE (5GB tier)"
    echo "   • MongoDB Atlas: FREE (512MB tier)"
    echo "   • OpenAI API: Pay per use (~$5-15/month)"
    echo "   • Total: ~$5-15/month"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Deploy your application: ./deploy-cheapest.sh"
    echo "   2. Access your chatbot: http://your-domain/docs"
    echo "   3. Monitor usage and costs"
else
    print_error "Configuration test failed!"
    echo ""
    echo "🔧 Please check:"
    echo "   1. All API keys are correct"
    echo "   2. Cloud services are accessible"
    echo "   3. Network connectivity"
fi
