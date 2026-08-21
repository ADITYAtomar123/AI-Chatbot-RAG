# 🤖 AI Chatbot

An intelligent AI-powered chatbot built with Python and Streamlit that supports normal conversations, document-based question answering, image analysis, voice input, internet search, memory, and data visualization.

## 🚀 Live Demo

[Open AI Chatbot](https://aditya-ai-chatbot.streamlit.app/)
## ✨ Features

### 💬 AI Chat
- Natural language conversations
- Chat history
- Create new conversations
- Rename conversations
- Delete conversations
- Regenerate AI responses
- Copy AI responses

### 📄 Document Understanding
- PDF upload and question answering
- RAG-based PDF search
- Source page references
- DOCX document support

### 📊 Data Analysis
- CSV file upload
- Excel file upload
- Data preview
- AI-based data questions
- Interactive charts
- Bar, Line, Pie and Scatter charts

### 🖼 Image Analysis
- Upload JPG, JPEG and PNG images
- Ask questions about images
- AI-powered image analysis

### 🎤 Voice Input
- Voice-based questions
- Speech-to-text support

### 🌐 Internet Search
- Optional internet search
- Current information retrieval
- AI-generated answers using search results

### 🧠 AI Memory
- Detects useful user information
- Stores memories
- Uses relevant memories in future conversations

### 🔐 Authentication
- User registration
- Login system
- Logout
- Password hashing

### 🏠 Dashboard
- Conversation statistics
- Document count
- Memory count
- Chart count
- Recent conversations

## 🛠️ Technologies Used

- Python
- Streamlit
- Groq
- LangChain
- FAISS
- HuggingFace Embeddings
- Google Gemini
- Plotly
- Pandas
- SQLite
- Python-docx
- SpeechRecognition
- DuckDuckGo Search

## 🧠 RAG Architecture

The PDF question-answering system uses Retrieval-Augmented Generation (RAG).

```text
PDF Upload
    ↓
PDF Text Extraction
    ↓
Text Chunking
    ↓
HuggingFace Embeddings
    ↓
FAISS Vector Database
    ↓
User Question
    ↓
Relevant Document Retrieval
    ↓
Groq LLM
    ↓
AI Answer