# YouTube Assistant RAG API

**Advanced AI-powered YouTube video analysis platform with comparative analysis and trend identification capabilities.**

**Developed by [Anjana Urulugastenna](https://anjanau.com/) - Quantitative Analyst & AI Engineer**

A production-ready YouTube video analysis service built with FastAPI, featuring AI-powered summarization, sentiment analysis, comparative analysis, trend analysis, and intelligent question-answering using Retrieval-Augmented Generation (RAG) architecture.

## 🚀 Features

### **Core Functionality**
- **YouTube Integration**: Fetch transcripts from any public YouTube video
- **AI-Powered Analysis**: Generate summaries using Google's Gemini AI
- **Intelligent Chat**: Converse with video content using RAG for contextual responses
- **Background Processing**: Non-blocking video analysis with status monitoring

### **Analysis Options**
- **Multiple Summary Types**: Comprehensive, executive, bullet points, key topics
- **Sentiment Analysis**: Understand the emotional tone of content
- **Key Topic Extraction**: Identify main themes and subjects
- **Suggested Questions**: AI-generated questions for deeper exploration

### **🆕 Advanced Analysis Features**
- **🔍 Comparative Analysis**: Compare 2-10 videos on similar topics to identify differences, similarities, and unique insights
- **📈 Trend Analysis**: Analyze patterns across 3-50 videos over time to track topic evolution and emerging themes
- **🤖 AI-Powered Insights**: Generate actionable insights from comparative and trend analysis
- **📊 Multi-Grouping Options**: Temporal, topical, or channel-based analysis grouping

### **API Features**
- **RESTful Endpoints**: Complete REST API for integration
- **Async Processing**: Background tasks for heavy operations
- **Caching System**: In-memory caching for improved performance
- **Auto Documentation**: Interactive API docs with Swagger/OpenAPI
- **Health Monitoring**: Real-time status and metrics endpoints
- **CORS Support**: Ready for web application integration

## 🏗️ Architecture

### **Backend (FastAPI)**
- **Production-grade** async API server
- **Background task processing** for video analysis
- **In-memory caching** for performance optimization
- **Comprehensive error handling** and validation
- **Automatic API documentation** generation

### **Frontend (Streamlit)**
- **Modern tabbed interface** with four main sections:
  - 🎬 **Single Video Analysis**: Traditional single video processing
  - ⚖️ **Compare Videos**: Side-by-side comparison of multiple videos
  - 📈 **Trend Analysis**: Multi-video trend identification and forecasting
  - 💬 **Chat Interface**: Interactive Q&A with analyzed content
- **Real-time status monitoring** of processing jobs
- **Interactive chat** with processed videos
- **Export functionality** for summaries, comparisons, and conversations
- **Dynamic URL management** for bulk video input

## 🛠️ Technology Stack

- **API Framework**: FastAPI with Pydantic validation
- **Frontend**: Streamlit with custom styling
- **AI Model**: Google Gemini 1.5 Flash
- **Vector Database**: FAISS for similarity search
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Document Processing**: LangChain for text chunking and retrieval
- **YouTube API**: youtube-transcript-api for transcript fetching
- **Async Runtime**: Uvicorn ASGI server

## Introduction: Installing Python on Windows

Before using the YouTube Video Assistant, you need to have Python installed on your system. Follow these steps to install Python 3.12 or later:

### Steps to Install Python

1. **Download Python:**
   - Visit the [official Python website](https://www.python.org/downloads/).
   - Click on the "Download Python 3.12.x" button (the latest version).

2. **Run the Installer:**
   - Open the downloaded installer.
   - Ensure you check the box that says "Add Python to PATH."
   - Click on "Install Now" and follow the prompts.

3. **Verify Installation:**
   - Open Command Prompt (cmd).
   - Type `python --version` and press Enter. You should see the Python version if installed correctly.

## Setup Instructions

### Prerequisites

- Python 3.12 or later
- Required libraries (install with `pip install -r requirements.txt`):
  - `streamlit`
  - `langchain`
  - `faiss-cpu`
  - `youtube-transcript-api`
  - `google-generativeai`

### Environment Variables

This project uses a `.env` file to store sensitive API keys. Ensure your `.env` file includes:

```plaintext
GOOGEL_API_KEY=<Your Google Gemini API Key>
```
## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+ 
- Google API Key for Gemini AI

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anju982/YoutubeAssistant_RAG.git
   cd YoutubeAssistant_RAG
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### **Running the Application**

#### **Option 1: FastAPI Backend + Streamlit Frontend (Recommended)**

**Start the API server:**
```bash
python -m uvicorn api:app --reload --port 8001
```

**Start the frontend (in new terminal):**
```bash
streamlit run frontend_api.py --server.port 8501
```

- **API Documentation**: http://localhost:8001/docs
- **Frontend Interface**: http://localhost:8501

#### **Option 2: API-Only (for Integration)**

```bash
python -m uvicorn api:app --reload --port 8001
```

Access interactive API docs at: http://localhost:8001/docs

## 📋 API Endpoints

### **Core Analysis**
- `POST /api/v1/analyze` - Analyze YouTube video
- `GET /api/v1/status/{video_id}` - Check processing status  
- `GET /api/v1/analysis/{video_id}` - Get analysis results

### **Chat & Interaction**
- `POST /api/v1/chat` - Chat with video content
- `GET /api/v1/sessions/{session_id}/history` - Get chat history

### **Management**
- `GET /health` - API health check
- `GET /api/v1/videos` - List processed videos
- `DELETE /api/v1/cache` - Clear cache

## 🧪 Testing

Run the included test suite:
```bash
python test_api.py
```

## 📚 Usage Examples

### **Analyze a Video (cURL)**
```bash
curl -X POST "http://localhost:8001/api/v1/analyze" 
     -H "Content-Type: application/json" 
     -d '{
       "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
       "summary_type": "comprehensive",
       "include_sentiment": true,
       "include_topics": true,
       "include_questions": true
     }'
```

### **Chat with Video (Python)**
```python
import requests

response = requests.post("http://localhost:8001/api/v1/chat", json={
    "session_id": "my_session",
    "message": "What are the main points discussed?",
    "use_external_sources": False
})

print(response.json()["response"])
```

## 🏗️ Project Structure

```
YoutubeAssistant_RAG/
├── api.py                 # FastAPI backend server
├── frontend_api.py        # Streamlit frontend
├── UIHelper.py           # Core business logic
├── test_api.py           # API test suite
├── requirements.txt      # Dependencies
├── FASTAPI_COMPARISON.md # Architecture comparison
└── README.md            # This file
```

## 🔧 Configuration

### **Environment Variables**
Create a `.env` file with:
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
```

### **API Configuration**
The FastAPI server can be configured via environment variables:
- `API_HOST`: Server host (default: 127.0.0.1)
- `API_PORT`: Server port (default: 8001)  
- `CACHE_SIZE`: Maximum cache entries (default: 100)

## 🐳 Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
```

```bash
# Build and run
docker build -t youtube-assistant .
docker run -p 8001:8001 -e GOOGLE_API_KEY=your_key youtube-assistant
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language understanding
- **FastAPI** for the robust API framework
- **Streamlit** for rapid frontend development
- **LangChain** for RAG implementation
- **FAISS** for efficient vector similarity search

## 📊 Performance & Scalability

- **Concurrent Processing**: Handle multiple video analyses simultaneously
- **Caching**: In-memory caching reduces processing time for repeated requests  
- **Background Tasks**: Non-blocking operations for better user experience
- **Resource Optimization**: Efficient memory and CPU usage patterns
- **Production Ready**: Designed for enterprise deployment with monitoring and logging

---

## 👨‍💻 Developer

**Anjana Urulugastenna**  
*Quantitative Analyst & AI Engineer*

� **Website:** [anjanau.com](https://anjanau.com/)  
💼 **Expertise:** AI/ML Engineering, Quantitative Analysis, Full-Stack Development  
🚀 **Specialization:** Advanced AI systems, RAG architectures, Financial Technology

---

## 📄 License & Copyright

**© 2025 Anjana Urulugastenna. All rights reserved.**

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software, via any medium, is strictly prohibited without the express written permission of Anjana Urulugastenna.

For licensing inquiries or commercial use, please contact via [anjanau.com](https://anjanau.com/).

---

## 🎯 Project Information

- **Project:** YouTube Assistant RAG API
- **Version:** 2.0.0
- **Status:** Production Ready
- **Last Updated:** July 2025
- **Technologies:** Python, FastAPI, Streamlit, Google Gemini AI, LangChain, FAISS
- **Architecture:** Microservices with RAG (Retrieval-Augmented Generation)

**�🎥 Start analyzing YouTube videos with AI-powered insights today!**

*Built with ❤️ by [Anjana Urulugastenna](https://anjanau.com/)*
