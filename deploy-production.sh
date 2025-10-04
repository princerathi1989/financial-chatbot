#!/bin/bash

# Production Deployment Script for Financial Multi-Agent Chatbot

set -e

echo "🚀 Starting production deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is required but not set in .env"
    exit 1
fi

echo "✅ Environment variables loaded"

# Create necessary directories
mkdir -p storage/chroma_db storage/uploads storage/temp logs

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations (if needed)
echo "🗄️ Setting up database..."

# Start the application
echo "🎯 Starting Financial Multi-Agent Chatbot..."
echo "📍 API will be available at: http://${API_HOST:-0.0.0.0}:${API_PORT:-8000}"
echo "📚 API Documentation: http://${API_HOST:-0.0.0.0}:${API_PORT:-8000}/docs"
echo "❤️ Health Check: http://${API_HOST:-0.0.0.0}:${API_PORT:-8000}/health"

# Start with production settings
python main.py
