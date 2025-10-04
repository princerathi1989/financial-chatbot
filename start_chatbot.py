#!/usr/bin/env python3
"""
Startup script for Financial Multi-Agent Chatbot
Runs both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import fastapi
        import uvicorn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "main.py"
    ], cwd=Path(__file__).parent)
    return backend_process

def start_frontend():
    """Start the Streamlit frontend."""
    print("🎨 Starting Streamlit frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ], cwd=Path(__file__).parent)
    return frontend_process

def wait_for_backend():
    """Wait for backend to be ready."""
    import requests
    max_retries = 30
    retry_count = 0
    
    print("⏳ Waiting for backend to start...")
    while retry_count < max_retries:
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        
        retry_count += 1
        time.sleep(1)
        print(f"⏳ Retrying... ({retry_count}/{max_retries})")
    
    print("❌ Backend failed to start")
    return False

def main():
    """Main startup function."""
    print("🤖 Financial Multi-Agent Chatbot Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        
        # Wait for backend to be ready
        if not wait_for_backend():
            print("❌ Failed to start backend")
            return
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("\n🎉 Both servers are starting up!")
        print("📡 Backend API: http://localhost:8000")
        print("🎨 Frontend UI: http://localhost:8501")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop both servers")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"❌ Process {i} has stopped unexpectedly")
                    return
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
