#!/usr/bin/env python3
"""
Financial Multi-Agent Chatbot - Streamlit UI

A WhatsApp-like interface for the Financial Multi-Agent Chatbot system.
Features:
- Modern chat interface with message bubbles
- Agent selection (RAG, Summarization, MCQ, Analytics)
- File upload for PDFs and CSVs
- Chat history and conversation management
- Real-time responses from the FastAPI backend
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
import base64
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Financial Multi-Agent Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for WhatsApp-like interface
st.markdown("""
<style>
    /* Main container styling */
    .main-container {
        background-color: #f0f2f6;
        padding: 0;
        margin: 0;
    }
    
    /* Chat container */
    .chat-container {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 20px;
        margin: 10px;
        height: 70vh;
        overflow-y: auto;
    }
    
    /* Message bubbles */
    .user-message {
        background-color: #dcf8c6;
        padding: 10px 15px;
        border-radius: 18px 18px 5px 18px;
        margin: 5px 0;
        margin-left: 20%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    .bot-message {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 5px;
        margin: 5px 0;
        margin-right: 20%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border: 1px solid #e5e5e5;
        word-wrap: break-word;
    }
    
    /* Agent indicator */
    .agent-indicator {
        font-size: 0.8em;
        color: #666;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    /* Timestamp */
    .message-time {
        font-size: 0.7em;
        color: #999;
        text-align: right;
        margin-top: 5px;
    }
    
    /* Input area */
    .input-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    
    /* File upload area */
    .upload-area {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 10px 0;
    }
    
    /* Agent selection buttons */
    .agent-button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .agent-button:hover {
        background-color: #0056b3;
    }
    
    .agent-button.selected {
        background-color: #28a745;
    }
    
    /* Status indicators */
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

class FinancialChatbotUI:
    """Main UI class for the Financial Multi-Agent Chatbot."""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.agents = {
            "RAG": {
                "name": "RAG Agent",
                "description": "Question-answering over financial documents",
                "icon": "📄",
                "color": "#007bff"
            },
            "SUMMARIZATION": {
                "name": "Summarization Agent", 
                "description": "Creates executive summaries with key quotes",
                "icon": "📊",
                "color": "#28a745"
            },
            "MCQ": {
                "name": "MCQ Agent",
                "description": "Generates assessment questions",
                "icon": "🧠",
                "color": "#ffc107"
            },
            "ANALYTICS": {
                "name": "Analytics Agent",
                "description": "Provides insights and data analysis",
                "icon": "📈",
                "color": "#dc3545"
            }
        }
    
    def check_api_health(self) -> bool:
        """Check if the API is running and healthy."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_message(self, message: str, agent_type: str, document_id: Optional[str] = None) -> Dict:
        """Send a message to the API and get response."""
        try:
            payload = {
                "message": message,
                "agent_type": agent_type.lower(),
                "document_id": document_id
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat", 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}
    
    def upload_multiple_files(self, files: List[bytes], filenames: List[str]) -> List[Dict]:
        """Upload multiple files to the API."""
        try:
            # Prepare files for upload - FastAPI expects multiple files with same field name
            file_data = []
            for file_content, filename in zip(files, filenames):
                file_data.append(("files", (filename, file_content, "application/octet-stream")))
            
            response = requests.post(f"{self.api_base_url}/upload/multiple", files=file_data, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            else:
                return [{"error": f"Upload failed: {response.text}"}]
                
        except Exception as e:
            return [{"error": f"Upload error: {str(e)}"}]
    
    def get_documents(self) -> List[Dict]:
        """Get list of uploaded documents."""
        try:
            response = requests.get(f"{self.api_base_url}/documents")
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def render_sidebar(self):
        """Render the sidebar with agent selection and file upload."""
        with st.sidebar:
            st.title("🤖 Financial Chatbot")
            
            # API Status
            st.markdown("### 📡 API Status")
            if self.check_api_health():
                st.markdown('<p class="status-online">🟢 Online</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-offline">🔴 Offline</p>', unsafe_allow_html=True)
                st.error("Please start the API server: `python main.py`")
                return
            
            # Agent Selection
            st.markdown("### 🎯 Select Agent")
            selected_agent = st.selectbox(
                "Choose your agent:",
                options=list(self.agents.keys()),
                format_func=lambda x: f"{self.agents[x]['icon']} {self.agents[x]['name']}"
            )
            
            # Agent Description
            if selected_agent:
                agent_info = self.agents[selected_agent]
                st.markdown(f"**{agent_info['description']}**")
            
            # File Upload Section
            st.markdown("### 📁 Upload Documents")
            
            # Multi-File Upload
            st.markdown("**📤 Upload Multiple Files**")
            uploaded_files = st.file_uploader(
                "Upload multiple PDFs and CSVs",
                type=['pdf', 'csv'],
                accept_multiple_files=True,
                key="multi_uploader",
                help="Select multiple PDF and CSV files to upload at once (max 10 files)"
            )
            
            if uploaded_files:
                if st.button("📤 Upload All Files", type="primary"):
                    if len(uploaded_files) > 10:
                        st.error("❌ Maximum 10 files allowed per upload")
                    else:
                        with st.spinner(f"Uploading {len(uploaded_files)} files..."):
                            # Prepare files for upload
                            files_content = []
                            filenames = []
                            
                            for file in uploaded_files:
                                files_content.append(file.read())
                                filenames.append(file.name)
                            
                            # Upload all files
                            results = self.upload_multiple_files(files_content, filenames)
                            
                            # Display results
                            successful_uploads = 0
                            failed_uploads = 0
                            
                            for i, result in enumerate(results):
                                if "error" not in result and result.get('status') == 'processed':
                                    st.success(f"✅ {result['filename']}")
                                    successful_uploads += 1
                                else:
                                    st.error(f"❌ {filenames[i]}: {result.get('error', 'Upload failed')}")
                                    failed_uploads += 1
                            
                            # Summary
                            if successful_uploads > 0:
                                st.success(f"🎉 Successfully uploaded {successful_uploads} files!")
                            if failed_uploads > 0:
                                st.warning(f"⚠️ {failed_uploads} files failed to upload")
            
            # Document List
            st.markdown("### 📋 Uploaded Documents")
            documents = self.get_documents()
            if documents:
                for doc in documents:
                    doc_type = "📄" if doc['file_type'] == 'pdf' else "📊"
                    st.markdown(f"{doc_type} {doc['filename']}")
            else:
                st.markdown("*No documents uploaded*")
            
            # Clear Chat Button
            st.markdown("### 🗑️ Actions")
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
            
            return selected_agent
    
    def render_chat_message(self, message: str, is_user: bool, agent_type: str = None, timestamp: str = None, sources: List = None):
        """Render a single chat message with enhanced styling."""
        if is_user:
            st.markdown(f"""
            <div class="user-message">
                {message}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            agent_info = ""
            if agent_type and agent_type in self.agents:
                agent_info = f'<div class="agent-indicator">{self.agents[agent_type]["icon"]} {self.agents[agent_type]["name"]}</div>'
            
            # Add sources if available
            sources_info = ""
            if sources and len(sources) > 0:
                sources_info = f'<div style="font-size: 0.8em; color: #666; margin-top: 5px;">📎 Sources: {len(sources)}</div>'
            
            st.markdown(f"""
            <div class="bot-message">
                {agent_info}
                {message}
                {sources_info}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_chat_interface(self, selected_agent: str):
        """Render the main chat interface."""
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            self.render_chat_message(
                message["content"],
                message["is_user"],
                message.get("agent_type"),
                message.get("timestamp"),
                message.get("sources")
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input area
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # Message input
        user_input = st.text_input(
            f"💬 Ask {self.agents[selected_agent]['name']}...",
            key="user_input",
            placeholder=f"Type your message for {self.agents[selected_agent]['name']}..."
        )
        
        # Send button
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            if st.button("📤 Send", type="primary"):
                if user_input.strip():
                    # Add user message to chat
                    timestamp = datetime.now().strftime("%H:%M")
                    st.session_state.messages.append({
                        "content": user_input,
                        "is_user": True,
                        "timestamp": timestamp
                    })
                    
                    # Get document ID based on agent type
                    document_id = None
                    if selected_agent in ["RAG", "SUMMARIZATION", "MCQ"]:
                        document_id = st.session_state.get("pdf_document_id")
                    elif selected_agent == "ANALYTICS":
                        document_id = st.session_state.get("csv_document_id")
                    
                    # Send to API and get response
                    with st.spinner(f"🤖 {self.agents[selected_agent]['name']} is thinking..."):
                        response = self.send_message(user_input, selected_agent, document_id)
                    
                    # Add bot response to chat
                    if "error" not in response:
                        bot_message = response.get("response", "No response received")
                        sources = response.get("sources", [])
                        st.session_state.messages.append({
                            "content": bot_message,
                            "is_user": False,
                            "agent_type": selected_agent,
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "sources": sources
                        })
                    else:
                        st.session_state.messages.append({
                            "content": f"❌ Error: {response['error']}",
                            "is_user": False,
                            "agent_type": selected_agent,
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "sources": []
                        })
                    
                    st.rerun()
        
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_welcome_screen(self):
        """Render welcome screen when no agent is selected."""
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1>🤖 Financial Multi-Agent Chatbot</h1>
            <h3>Welcome to your AI-powered financial assistant!</h3>
            <p style="font-size: 18px; color: #666;">
                Select an agent from the sidebar to start chatting and upload your financial documents.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📄 Document Analysis
            - Upload PDF financial reports
            - Ask questions about your documents
            - Get executive summaries
            - Generate assessment questions
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Data Analytics
            - Upload CSV financial data
            - Get insights and trends
            - Calculate KPIs
            - Detect anomalies
            """)
    
    def run(self):
        """Main application runner."""
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #007bff, #28a745); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🤖 Financial Multi-Agent Chatbot</h1>
            <p>AI-powered financial document analysis and insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Render sidebar and get selected agent
        selected_agent = self.render_sidebar()
        
        # Main content area
        if selected_agent:
            self.render_chat_interface(selected_agent)
        else:
            self.render_welcome_screen()

def main():
    """Main function to run the Streamlit app."""
    app = FinancialChatbotUI()
    app.run()

if __name__ == "__main__":
    main()
