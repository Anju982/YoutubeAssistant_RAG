"""
Streamlit Frontend for FastAPI Backend
This demonstrates how to use the FastAPI backend with a Streamlit frontend
"""

import streamlit as st
import requests
import time
from typing import Dict, Any, List
from datetime import datetime

# FastAPI backend URL (adjust as needed)
API_BASE_URL = "http://localhost:8001"

# Page configuration
st.set_page_config(
    page_title="🎥 YouTube Assistant - AI Video Analysis Platform",
    page_icon="🎥", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://anjanau.com/',
        'Report a bug': 'https://anjanau.com/',
        'About': "AI-Powered YouTube Video Analysis Platform by Anjana Urulugastenna"
    }
)

# Custom CSS with professional styling matching anjanau.com
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styles */
.stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    color: #e0e0e0;
}

/* Dark theme for main containers */
.main > div {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
}

/* Header Styling */
.main-header {
    background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: #f0f2f5;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    border: 1px solid #3d4a6a;
}

.main-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-header .subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin-top: 0.5rem;
    font-weight: 400;
}

.main-header .creator-info {
    margin-top: 1rem;
    font-size: 0.95rem;
    opacity: 0.8;
}

/* API Status Styles */
.api-status {
    padding: 0.8rem;
    border-radius: 10px;
    margin: 0.8rem 0;
    font-weight: 500;
    text-align: center;
}

.status-healthy { 
    background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%);
    color: #f0f2f5;
    border: 2px solid #4c72c4;
}

.status-processing { 
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    color: #f0f2f5;
    border: 2px solid #e74c3c;
}

.status-error { 
    background: linear-gradient(135deg, #d35400 0%, #e67e22 100%);
    color: #f0f2f5;
    border: 2px solid #d35400;
}

/* Chat Message Styles */
.chat-message { 
    padding: 1.2rem; 
    margin: 0.8rem 0; 
    border-radius: 15px; 
    border-left: 4px solid #4c72c4;
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    color: #e0e0e0;
}

/* Sidebar Styling */
.css-1d391kg {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%) !important;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%);
    color: #f0f2f5;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(76, 114, 196, 0.3);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 114, 196, 0.4);
}
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border-radius: 10px;
    padding: 0.5rem;
    border: 1px solid #3d4a6a;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.8rem 1.5rem;
    font-weight: 500;
    background: #34495e;
    color: #bdc3c7;
    border: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%);
    color: #f0f2f5;
    border: 2px solid #4c72c4;
}

/* Metric Styling */
.metric-container {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    border-left: 4px solid #4c72c4;
    border: 1px solid #3d4a6a;
    margin: 1rem 0;
    color: #e0e0e0;
}

/* Progress Bar Styling */
.stProgress > div > div > div > div {
    background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%);
}

/* Footer Cards Styling */
.footer-card {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #3d4a6a;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
}

.footer-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(76, 114, 196, 0.2);
}

.card-header {
    text-align: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #4c72c4;
}

.card-header h4 {
    color: #4c72c4;
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
}

.card-content {
    color: #e0e0e0;
    text-align: center;
}

.card-content p {
    margin: 0.5rem 0;
    font-size: 0.9rem;
    line-height: 1.4;
}

.card-content strong {
    color: #f0f2f5;
    font-weight: 600;
}

.card-features {
    margin-top: 1rem;
    text-align: left;
    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 3px solid #4c72c4;
    font-size: 0.85rem;
    line-height: 1.6;
    color: #bdc3c7;
}

.developer-info {
    margin-top: 1rem;
    text-align: left;
    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 3px solid #27ae60;
    font-size: 0.85rem;
    line-height: 1.6;
}

.developer-info p {
    margin: 0.3rem 0;
    color: #bdc3c7;
}

.tech-stack {
    margin-top: 1rem;
    text-align: left;
    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 3px solid #e74c3c;
    font-size: 0.85rem;
    line-height: 1.6;
}

.tech-stack p {
    margin: 0.4rem 0;
    color: #bdc3c7;
}

.tech-stack strong {
    color: #f0f2f5;
}

.footer-link {
    color: #74a7ff;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: #5a67d8;
    text-decoration: none;
}

.copyright-card {
    background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%);
    color: #f0f2f5;
    text-align: center;
    padding: 1rem 2rem;
    border-radius: 25px;
    margin: 2rem auto 1rem auto;
    max-width: 600px;
    box-shadow: 0 4px 20px rgba(76, 114, 196, 0.3);
    border: 1px solid #3d4a6a;
}

.copyright-card p {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 500;
}

/* Mobile responsive footer cards */
@media (max-width: 768px) {
    .footer-card {
        margin-bottom: 1.5rem;
        padding: 1.2rem;
    }
    
    .card-features,
    .developer-info,
    .tech-stack {
        font-size: 0.8rem;
        padding: 0.8rem;
    }
    
    .copyright-card {
        margin: 1.5rem auto;
        padding: 0.8rem 1rem;
    }
    
    .copyright-card p {
        font-size: 0.8rem;
    }
}

/* Info Box Styling */
.stInfo {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border-left: 4px solid #4c72c4;
    color: #e0e0e0;
}

/* Success Box Styling */
.stSuccess {
    background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
    border-left: 4px solid #27ae60;
    color: #f0f2f5;
}

/* Warning Box Styling */
.stWarning {
    background: linear-gradient(135deg, #d35400 0%, #e67e22 100%);
    border-left: 4px solid #d35400;
    color: #f0f2f5;
}

/* Error Box Styling */
.stError {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    border-left: 4px solid #e74c3c;
    color: #f0f2f5;
}

/* Card-like containers */
.analysis-card {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.3);
    border: 1px solid #3d4a6a;
    margin: 1rem 0;
    color: #e0e0e0;
}

/* Input Field Styling */
.stTextInput > div > div > input {
    background: #34495e;
    color: #e0e0e0;
    border: 2px solid #3d4a6a;
    border-radius: 10px;
}

.stTextInput > div > div > input:focus {
    border-color: #4c72c4;
    box-shadow: 0 0 0 2px rgba(76, 114, 196, 0.2);
}

/* Text Area Styling */
.stTextArea > div > div > textarea {
    background: #34495e;
    color: #e0e0e0;
    border: 2px solid #3d4a6a;
    border-radius: 10px;
}

.stTextArea > div > div > textarea:focus {
    border-color: #4c72c4;
    box-shadow: 0 0 0 2px rgba(76, 114, 196, 0.2);
}

/* Select Box Styling */
.stSelectbox > div > div > div {
    background: #34495e;
    color: #e0e0e0;
    border: 2px solid #3d4a6a;
}

/* Multiselect Styling */
.stMultiSelect > div > div > div {
    background: #34495e;
    color: #e0e0e0;
    border: 2px solid #3d4a6a;
}

/* Comprehensive Streamlit Component Dark Theme Overrides */
/* Main app background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%) !important;
}

/* Main content area */
[data-testid="stMain"] {
    background: transparent !important;
}

/* Header area */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%) !important;
}

[data-testid="stSidebar"] > div {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
}

/* All containers */
.stContainer, .block-container {
    background: transparent !important;
}

/* Columns */
[data-testid="column"] {
    background: transparent !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
    border: 1px solid #3d4a6a !important;
    color: #e0e0e0 !important;
}

/* Code blocks */
[data-testid="stCodeBlock"] {
    background: #2c3e50 !important;
    color: #e0e0e0 !important;
}

/* Markdown */
[data-testid="stMarkdown"] {
    color: #e0e0e0 !important;
}

/* Data frames */
[data-testid="stDataFrame"] {
    background: #2c3e50 !important;
    color: #e0e0e0 !important;
}

/* JSON */
[data-testid="stJson"] {
    background: #2c3e50 !important;
    color: #e0e0e0 !important;
}

/* All text elements */
.stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
    color: #e0e0e0 !important;
}

/* Override any remaining white backgrounds */
* {
    background-color: transparent !important;
}

.main > div, .main .block-container, .reportview-container {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%) !important;
}

/* Comprehensive Sidebar Dark Theme Styling */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%) !important;
}

.css-1y4p8pa, [data-testid="stSidebar"] > div {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
    color: #e0e0e0 !important;
}

/* Sidebar content styling */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #34495e !important;
    color: #e0e0e0 !important;
    border: 2px solid #3d4a6a !important;
}

[data-testid="stSidebar"] .stCheckbox > label {
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] .stMarkdown {
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 {
    color: #f0f2f5 !important;
}
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2rem;
    }
    
    .main-header .subtitle {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

def check_api_health() -> bool:
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def analyze_video_api(url: str, summary_type: str, sentiment: bool, topics: bool, questions: bool) -> Dict[str, Any]:
    """Call the FastAPI analyze endpoint"""
    payload = {
        "url": url,
        "summary_type": summary_type,
        "include_sentiment": sentiment,
        "include_topics": topics,
        "include_questions": questions
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/analyze", json=payload)
    response.raise_for_status()
    return response.json()

def get_analysis_status(video_id: str) -> Dict[str, Any]:
    """Get video analysis status"""
    response = requests.get(f"{API_BASE_URL}/api/v1/status/{video_id}")
    response.raise_for_status()
    return response.json()

def get_analysis_results(video_id: str, summary_type: str) -> Dict[str, Any]:
    """Get completed analysis results"""
    response = requests.get(f"{API_BASE_URL}/api/v1/analysis/{video_id}?summary_type={summary_type}")
    response.raise_for_status()
    return response.json()

def chat_with_video_api(session_id: str, message: str, external_sources: bool) -> Dict[str, Any]:
    """Send chat message to API"""
    payload = {
        "session_id": session_id,
        "message": message,
        "use_external_sources": external_sources
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/chat", json=payload)
    response.raise_for_status()
    return response.json()

def compare_videos_api(video_urls: List[str], aspects: List[str], depth: str) -> Dict[str, Any]:
    """Compare multiple videos"""
    payload = {
        "video_urls": video_urls,
        "comparison_aspects": aspects,
        "analysis_depth": depth
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/compare", json=payload)
    response.raise_for_status()
    return response.json()

def get_comparison_results(comparison_id: str) -> Dict[str, Any]:
    """Get comparison results"""
    response = requests.get(f"{API_BASE_URL}/api/v1/compare/{comparison_id}")
    response.raise_for_status()
    return response.json()

def analyze_trends_api(video_urls: List[str], time_period: str, aspects: List[str], grouping: str) -> Dict[str, Any]:
    """Analyze trends across multiple videos"""
    payload = {
        "video_urls": video_urls,
        "time_period": time_period,
        "trend_aspects": aspects,
        "grouping": grouping
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/trends", json=payload)
    response.raise_for_status()
    return response.json()

def get_trend_results(analysis_id: str) -> Dict[str, Any]:
    """Get trend analysis results"""
    response = requests.get(f"{API_BASE_URL}/api/v1/trends/{analysis_id}")
    response.raise_for_status()
    return response.json()

def main():
    # Professional Header with Personal Branding
    st.markdown("""
    <div class="main-header">
        <h1>🎥 YouTube Assistant</h1>
        <div class="subtitle">AI-Powered Video Analysis Platform</div>
        <div class="creator-info">
            Developed by <strong>Anjana Urulugastenna</strong><br>
            Quantitative Analyst & AI Engineer | <a href="https://anjanau.com/" target="_blank" class="website-link">anjanau.com</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("❌ FastAPI backend is not running! Please start it with: `./start.sh backend`")
        st.stop()
    else:
        st.success("✅ Connected to FastAPI backend")
    
    # Initialize session state
    if 'video_id' not in st.session_state:
        st.session_state.video_id = None
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"
    if 'comparison_data' not in st.session_state:
        st.session_state.comparison_data = None
    if 'trend_data' not in st.session_state:
        st.session_state.trend_data = None
    
    # Main Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎬 Single Video Analysis", 
        "⚖️ Compare Videos", 
        "📈 Trend Analysis", 
        "💬 Chat Interface"
    ])
    
    with tab1:
        render_single_video_tab()
    
    with tab2:
        render_comparison_tab()
    
    with tab3:
        render_trend_analysis_tab()
    
    with tab4:
        render_chat_tab()
    
    # Separate Footer Cards
    st.markdown("---")
    st.markdown("### 📊 Platform Information")
    
    # Create three columns for footer cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="footer-card">
            <div class="card-header">
                <h4>🎥 YouTube Assistant</h4>
            </div>
            <div class="card-content">
                <p><strong>AI-Powered Video Analysis Platform</strong></p>
                <p>Advanced analysis, comparison, and trend identification for YouTube videos using cutting-edge AI technology.</p>
                <div class="card-features">
                    • Single Video Analysis<br>
                    • Multi-Video Comparison<br>
                    • Trend Analysis<br>
                    • AI Chat Interface
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="footer-card">
            <div class="card-header">
                <h4>👨‍💻 Developer</h4>
            </div>
            <div class="card-content">
                <p><strong>Anjana Urulugastenna</strong></p>
                <p>Quantitative Analyst & AI Engineer</p>
                <div class="developer-info">
                    <p>📧 Professional Contact</p>
                    <p>🌐 <a href="https://anjanau.com/" target="_blank" class="footer-link">anjanau.com</a></p>
                    <p>🔬 Specializing in AI/ML, Data Analysis, and Quantitative Research</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="footer-card">
            <div class="card-header">
                <h4>⚙️ Technology Stack</h4>
            </div>
            <div class="card-content">
                <p><strong>Powered by Advanced Technologies</strong></p>
                <div class="tech-stack">
                    <p>🔧 <strong>Backend:</strong> FastAPI + Python</p>
                    <p>🎨 <strong>Frontend:</strong> Streamlit</p>
                    <p>🤖 <strong>AI Engine:</strong> Google Gemini AI</p>
                    <p>🔗 <strong>Framework:</strong> LangChain</p>
                    <p>📊 <strong>Vector DB:</strong> FAISS</p>
                    <p>🧠 <strong>Architecture:</strong> RAG (Retrieval-Augmented Generation)</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Copyright card at the bottom
    st.markdown("""
    <div class="copyright-card">
        <p>© 2025 Anjana Urulugastenna • All Rights Reserved • Powered by AI Innovation</p>
    </div>
    """, unsafe_allow_html=True)

def render_single_video_tab():
    """Render the single video analysis tab"""
    # Professional Sidebar configuration
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4c72c4 0%, #5a67d8 100%); 
                    color: #f0f2f5; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;
                    border: 1px solid #3d4a6a; box-shadow: 0 4px 15px rgba(76, 114, 196, 0.3);">
            <h3 style="margin: 0; color: #f0f2f5;">🎯 Analysis Settings</h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; color: #e8e8e8;">Configure your video analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        summary_type = st.selectbox(
            "📝 Summary Type",
            ["comprehensive", "executive", "bullet_points", "key_topics"],
            help="Choose the type of summary you want"
        )
        
        st.markdown("### 📊 Analysis Features")
        include_sentiment = st.checkbox("😊 Sentiment Analysis", value=False, help="Analyze emotional tone")
        include_topics = st.checkbox("🎯 Key Topics", value=True, help="Extract main themes")
        include_questions = st.checkbox("❓ Suggested Questions", value=True, help="Generate relevant questions")
        
        st.markdown("### 🔧 System Status")
        if st.button("🔄 Refresh Status", help="Check system status"):
            st.rerun()
        
        # Show processed videos with professional styling
        try:
            videos_response = requests.get(f"{API_BASE_URL}/api/v1/videos")
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                st.markdown(f"""
                <div class="metric-container">
                    <h4 style="margin: 0; color: #4c72c4;">📊 System Metrics</h4>
                    <p style="margin: 0.5rem 0 0 0;">Processed Videos: <strong>{videos_data['total']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            st.markdown("""
            <div class="metric-container" style="border-left-color: #ffc107;">
                <h4 style="margin: 0; color: #ffc107;">⚠️ Status Unknown</h4>
                <p style="margin: 0.5rem 0 0 0;">Could not fetch video count</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Professional branding in sidebar
        st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                    border-radius: 10px; text-align: center; border: 1px solid #3d4a6a; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <small style="color: #e0e0e0;"><strong style="color: #f0f2f5;">Developed by</strong><br>
            <span style="color: #bdc3c7;">Anjana Urulugastenna</span><br>
            <a href="https://anjanau.com/" target="_blank" style="color: #74a7ff; text-decoration: none;">anjanau.com</a></small>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content with professional styling
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="analysis-card">
            <h2 style="color: #4c72c4; margin-top: 0;">🎬 Video Analysis</h2>
            <p>Analyze any YouTube video with advanced AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Video input with enhanced styling
        video_url = st.text_input(
            "🔗 YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any public YouTube video URL"
        )
        
        if st.button("🚀 Analyze Video", type="primary", help="Start AI-powered video analysis"):
            if video_url:
                try:
                    with st.spinner("🎯 Starting analysis..."):
                        result = analyze_video_api(
                            video_url, 
                            summary_type, 
                            include_sentiment, 
                            include_topics, 
                            include_questions
                        )
                        
                        st.session_state.video_id = result["video_id"]
                        st.session_state.session_id = f"{result['video_id']}_{int(time.time())}"
                        
                        if result["status"] == "processing":
                            st.info("⏳ Video analysis started! Check status below.")
                        elif result["status"] == "already_processed":
                            st.success("✅ Video already processed!")
                            
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ API Error: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a YouTube URL")
        
        # Enhanced status monitoring
        if st.session_state.video_id:
            st.markdown("""
            <div class="analysis-card">
                <h3 style="color: #4c72c4; margin-top: 0;">📊 Analysis Status</h3>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                status_data = get_analysis_status(st.session_state.video_id)
                
                if status_data["status"] == "completed":
                    st.markdown('<div class="api-status status-healthy">✅ Analysis Complete</div>', unsafe_allow_html=True)
                    
                    # Get analysis results
                    if st.button("📖 Load Results", help="Load comprehensive analysis results"):
                        try:
                            analysis_data = get_analysis_results(st.session_state.video_id, summary_type)
                            st.session_state.analysis_data = analysis_data
                            st.success("✅ Results loaded successfully!")
                        except requests.exceptions.HTTPError as e:
                            if e.response.status_code == 202:
                                st.warning("⏳ Analysis still processing...")
                            else:
                                st.error(f"❌ Error loading results: {e}")
                        
                elif status_data["status"] == "processing":
                    st.markdown('<div class="api-status status-processing">⏳ Processing...</div>', unsafe_allow_html=True)
                    if st.button("🔄 Refresh Status", key="refresh_single"):
                        st.rerun()
                        
                elif status_data["status"] == "error":
                    st.markdown('<div class="api-status status-error">❌ Processing Error</div>', unsafe_allow_html=True)
                    st.error(f"Error: {status_data.get('error', 'Unknown error')}")
                
                # Show metadata with professional styling
                if status_data.get("metadata"):
                    metadata = status_data["metadata"]
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4 style="margin: 0; color: #4c72c4;">📺 Video Information</h4>
                        <p style="margin: 0.5rem 0 0 0;"><strong>Title:</strong> {metadata.get('title', 'Unknown')}</p>
                        <p style="margin: 0.5rem 0 0 0;"><strong>Channel:</strong> {metadata.get('author_name', 'Unknown')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Could not get status: {e}")
        
        # Display analysis results with enhanced styling
        if st.session_state.analysis_data:
            render_analysis_results(st.session_state.analysis_data)

def render_comparison_tab():
    """Render the video comparison tab"""
    st.markdown("""
    <div class="analysis-card">
        <h2 style="color: #4c72c4; margin-top: 0;">⚖️ Compare Multiple Videos</h2>
        <p><em>Compare 2-10 videos on similar topics to identify differences, similarities, and unique insights powered by advanced AI analysis.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Video URLs input with professional styling
    st.markdown("""
    <div class="analysis-card">
        <h3 style="color: #4c72c4; margin-top: 0;">📺 Videos to Compare</h3>
        <p>Add YouTube URLs for videos you want to compare (minimum 2, maximum 10)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize comparison URLs in session state
    if 'comparison_urls' not in st.session_state:
        st.session_state.comparison_urls = ["", ""]
    
    # Dynamic URL inputs
    for i in range(len(st.session_state.comparison_urls)):
        st.session_state.comparison_urls[i] = st.text_input(
            f"🔗 Video {i+1} URL", 
            value=st.session_state.comparison_urls[i],
            key=f"comp_url_{i}",
            placeholder="https://www.youtube.com/watch?v=...",
            help=f"YouTube URL for video {i+1}"
        )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Video", help="Add another video to compare (max 10)") and len(st.session_state.comparison_urls) < 10:
            st.session_state.comparison_urls.append("")
            st.rerun()
    
    with col2:
        if st.button("➖ Remove Video", help="Remove the last video") and len(st.session_state.comparison_urls) > 2:
            st.session_state.comparison_urls.pop()
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear All", help="Clear all video URLs"):
            st.session_state.comparison_urls = ["", ""]
            st.rerun()
    
    # Comparison settings with professional styling
    st.markdown("""
    <div class="analysis-card">
        <h3 style="color: #4c72c4; margin-top: 0;">⚙️ Comparison Settings</h3>
        <p>Configure how you want the videos to be compared</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        comparison_aspects = st.multiselect(
            "📊 Aspects to Compare",
            ["topics", "sentiment", "key_points", "conclusions", "approach", "depth", "audience"],
            default=["topics", "sentiment", "key_points", "conclusions"],
            help="Select which aspects of the videos to compare"
        )
    
    with col2:
        analysis_depth = st.selectbox(
            "🔍 Analysis Depth",
            ["comprehensive", "quick", "detailed"],
            index=0,
            help="Choose the depth of analysis"
        )
    
    # Start comparison with enhanced button
    if st.button("🔍 Start Comparison", type="primary", help="Begin AI-powered video comparison"):
        valid_urls = [url for url in st.session_state.comparison_urls if url.strip()]
        
        if len(valid_urls) < 2:
            st.error("❌ Please provide at least 2 valid YouTube URLs")
        else:
            try:
                with st.spinner("🔄 Starting video comparison..."):
                    result = compare_videos_api(valid_urls, comparison_aspects, analysis_depth)
                    st.session_state.comparison_id = result["comparison_id"]
                    st.success("✅ Comparison started! Monitor progress below.")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error starting comparison: {str(e)}")
    
    # Show comparison results with professional styling
    if hasattr(st.session_state, 'comparison_id'):
        st.markdown("""
        <div class="analysis-card">
            <h3 style="color: #4c72c4; margin-top: 0;">📊 Comparison Progress</h3>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            comparison_data = get_comparison_results(st.session_state.comparison_id)
            
            if comparison_data["status"] == "completed":
                st.markdown('<div class="api-status status-healthy">✅ Comparison completed!</div>', unsafe_allow_html=True)
                st.session_state.comparison_data = comparison_data
                
                # Display results with enhanced styling
                if comparison_data.get("comparison_results"):
                    st.markdown("""
                    <div class="analysis-card">
                        <h3 style="color: #4c72c4; margin-top: 0;">🔍 Comparison Results</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Videos analyzed
                    videos = comparison_data.get("videos", [])
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4 style="margin: 0; color: #4c72c4;">📺 Analysis Summary</h4>
                        <p style="margin: 0.5rem 0 0 0;"><strong>Videos Analyzed:</strong> {len(videos)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📺 Videos Overview", expanded=True):
                        for i, video in enumerate(videos, 1):
                            metadata = video.get("metadata", {})
                            st.markdown(f"""
                            <div style="padding: 1rem; margin: 0.5rem 0; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 10px; border-left: 4px solid #4c72c4; color: #e0e0e0;">
                                <strong>{i}. {metadata.get('title', 'Unknown Title')}</strong><br>
                                <small style="color: #bdc3c7;">📺 Channel: {metadata.get('author_name', 'Unknown')}</small><br>
                                <small style="color: #bdc3c7;">🔗 <a href="{video.get('url', '#')}" target="_blank" style="color: #74a7ff;">View Video</a></small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Comparison analysis
                    analysis = comparison_data["comparison_results"].get("comparison_analysis", "")
                    if analysis:
                        st.markdown("""
                        <div class="analysis-card">
                            <h3 style="color: #4c72c4; margin-top: 0;">📋 Detailed Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(analysis)
                    
                    # Summary stats
                    stats = comparison_data["comparison_results"].get("summary_stats", {})
                    if stats:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📺 Total Videos", stats.get("total_videos", 0))
                        with col2:
                            st.metric("📺 Channels", stats.get("channels", 0))
                        with col3:
                            st.metric("🎯 Topics Covered", stats.get("topics_covered", 0))
                
            elif comparison_data["status"] == "processing":
                progress = len(comparison_data.get("videos", []))
                total = len([url for url in st.session_state.comparison_urls if url.strip()])
                st.progress(progress / total if total > 0 else 0)
                st.markdown(f'<div class="api-status status-processing">⏳ Processing... ({progress}/{total} videos analyzed)</div>', unsafe_allow_html=True)
                
                if st.button("🔄 Refresh Progress", key="refresh_comparison"):
                    st.rerun()
                    
            elif comparison_data["status"] == "error":
                st.markdown(f'<div class="api-status status-error">❌ Comparison failed: {comparison_data.get("error", "Unknown error")}</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Error getting comparison results: {str(e)}")

def render_trend_analysis_tab():
    """Render the trend analysis tab"""
    st.header("📈 Trend Analysis")
    st.markdown("*Analyze trends and patterns across multiple videos over time to identify emerging themes and changes.*")
    
    # Video URLs input
    st.subheader("📺 Videos for Trend Analysis")
    st.info("💡 For best results, provide 5+ videos. You can analyze up to 50 videos at once.")
    
    # Initialize trend URLs in session state
    if 'trend_urls' not in st.session_state:
        st.session_state.trend_urls = ["", "", ""]
    
    # URL input area
    trend_urls_text = st.text_area(
        "YouTube URLs (one per line)",
        value="\n".join(st.session_state.trend_urls),
        height=200,
        placeholder="https://www.youtube.com/watch?v=example1\nhttps://www.youtube.com/watch?v=example2\nhttps://www.youtube.com/watch?v=example3"
    )
    
    # Parse URLs
    if trend_urls_text:
        st.session_state.trend_urls = [url.strip() for url in trend_urls_text.split('\n') if url.strip()]
    
    st.write(f"📊 **Videos to analyze:** {len([url for url in st.session_state.trend_urls if url])}")
    
    # Trend analysis settings
    st.subheader("⚙️ Analysis Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        time_period = st.selectbox(
            "Time Period Focus",
            ["all", "recent", "quarterly", "monthly"],
            help="How to group videos temporally"
        )
        
        trend_aspects = st.multiselect(
            "Trend Aspects",
            ["topics", "sentiment", "content_style", "engagement_patterns", "complexity", "audience_targeting"],
            default=["topics", "sentiment", "engagement_patterns"]
        )
    
    with col2:
        grouping_method = st.selectbox(
            "Grouping Method",
            ["temporal", "topical", "channel"],
            help="How to group videos for analysis"
        )
        
        min_videos = st.number_input(
            "Minimum Videos Required",
            min_value=3,
            max_value=50,
            value=5
        )
    
    # Start trend analysis
    if st.button("📊 Start Trend Analysis", type="primary"):
        valid_urls = [url for url in st.session_state.trend_urls if url]
        
        if len(valid_urls) < min_videos:
            st.error(f"❌ Please provide at least {min_videos} valid YouTube URLs")
        elif len(valid_urls) > 50:
            st.error("❌ Maximum 50 videos allowed for trend analysis")
        else:
            try:
                with st.spinner("📈 Starting trend analysis..."):
                    result = analyze_trends_api(valid_urls, time_period, trend_aspects, grouping_method)
                    st.session_state.trend_analysis_id = result["analysis_id"]
                    st.success("✅ Trend analysis started! Monitor progress below.")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error starting trend analysis: {str(e)}")
    
    # Show trend analysis results
    if hasattr(st.session_state, 'trend_analysis_id'):
        st.subheader("📊 Analysis Progress")
        
        try:
            trend_data = get_trend_results(st.session_state.trend_analysis_id)
            
            if trend_data["status"] == "completed":
                st.success("✅ Trend analysis completed!")
                st.session_state.trend_data = trend_data
                
                # Display results
                st.subheader("📈 Trend Analysis Results")
                
                # Progress metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Videos Analyzed", trend_data.get("videos_analyzed", 0))
                with col2:
                    st.metric("Trends Identified", len(trend_data.get("trends", {})))
                with col3:
                    st.metric("Key Insights", len(trend_data.get("insights", [])))
                
                # Trends
                trends = trend_data.get("trends", {})
                if trends and trends.get("trend_analysis"):
                    st.subheader("🔍 Detailed Trend Analysis")
                    st.markdown(trends["trend_analysis"])
                
                # Key insights
                insights = trend_data.get("insights", [])
                if insights:
                    st.subheader("💡 Key Insights")
                    for i, insight in enumerate(insights, 1):
                        st.write(f"**{i}.** {insight}")
                
                # Data summary
                data_summary = trends.get("data_summary", {})
                if data_summary:
                    with st.expander("📊 Analysis Summary"):
                        st.json(data_summary)
                
            elif trend_data["status"] == "processing":
                progress = trend_data.get("videos_analyzed", 0)
                total = len([url for url in st.session_state.trend_urls if url])
                
                if total > 0:
                    st.progress(progress / total)
                    st.info(f"⏳ Processing... ({progress}/{total} videos analyzed)")
                else:
                    st.info("⏳ Starting analysis...")
                
                if st.button("🔄 Refresh Progress", key="trend_refresh"):
                    st.rerun()
                    
            elif trend_data["status"] == "error":
                st.error(f"❌ Trend analysis failed: {trend_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"❌ Error getting trend analysis results: {str(e)}")

def render_chat_tab():
    """Render the chat interface tab"""
    st.markdown("""
    <div class="analysis-card">
        <h2 style="color: #4c72c4; margin-top: 0;">💬 Chat with Analyzed Videos</h2>
        <p>Interactive Q&A with your analyzed video content using advanced RAG (Retrieval-Augmented Generation)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.video_id:
        st.markdown("""
        <div class="analysis-card" style="text-align: center; border-left-color: #ffc107;">
            <h3 style="color: #ffc107; margin-top: 0;">🎬 No Videos Analyzed Yet</h3>
            <p>To start chatting, first analyze a video using one of these options:</p>
            <div style="margin: 1.5rem 0;">
                <p>📺 <strong>Single Video Analysis</strong> - Analyze individual videos</p>
                <p>⚖️ <strong>Compare Videos</strong> - Compare multiple videos</p>
                <p>📈 <strong>Trend Analysis</strong> - Analyze video trends</p>
            </div>
            <p><em>Once analysis is complete, return here to chat with the content!</em></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Chat settings
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem; 
                        border: 1px solid #3d4a6a; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <h4 style="margin: 0; color: #4c72c4;">💡 Chat Tips</h4>
                <p style="margin: 0.5rem 0 0 0; color: #bdc3c7;">Ask about video content, request summaries, or explore topics in depth</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            external_sources = st.checkbox("🌐 External Sources", value=False, 
                                         help="Include external knowledge in responses")
        
        # Chat interface with professional styling
        chat_container = st.container()
        
        # Display chat history with enhanced styling
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                # User message
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: #f8f9fa; padding: 1rem; border-radius: 15px; margin: 1rem 0;">
                    <strong>🧑 You:</strong><br>{chat["user"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Assistant message
                st.markdown(f"""
                <div class="chat-message">
                    <strong>🤖 AI Assistant:</strong><br>{chat["assistant"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_message = st.chat_input("💬 Ask anything about the analyzed videos...")
        
        # Handle pending question from suggested questions
        if hasattr(st.session_state, 'pending_question'):
            user_message = st.session_state.pending_question
            delattr(st.session_state, 'pending_question')
        
        if user_message:
            # Add user message to history
            st.session_state.chat_history.append({
                "user": user_message,
                "assistant": "..."
            })
            
            try:
                with st.spinner("🤔 AI is thinking..."):
                    chat_response = chat_with_video_api(
                        st.session_state.session_id,
                        user_message,
                        external_sources
                    )
                    
                    # Update the last assistant message
                    st.session_state.chat_history[-1]["assistant"] = chat_response["response"]
                    
                    # Show processing time
                    st.caption(f"⚡ Processed in {chat_response['processing_time']:.2f}s")
                    
                    st.rerun()
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Chat Error: {e}")
                # Remove the incomplete chat entry
                st.session_state.chat_history.pop()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.pop()
        
        # Chat controls with professional styling
        if st.session_state.chat_history:
            st.markdown("---")
            col_clear, col_export = st.columns(2)
            
            with col_clear:
                if st.button("🗑️ Clear Chat History", help="Clear all chat messages"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col_export:
                if st.button("📥 Export Chat", help="Download chat history as markdown"):
                    chat_text = f"""# Chat History - YouTube Assistant
**Generated by:** Anjana Urulugastenna's AI Video Analysis Platform
**Website:** https://anjanau.com/
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
                    for chat in st.session_state.chat_history:
                        chat_text += f"**🧑 You:** {chat['user']}\n\n"
                        chat_text += f"**🤖 AI Assistant:** {chat['assistant']}\n\n---\n\n"
                    
                    chat_text += """
---
*Powered by YouTube Assistant - AI Video Analysis Platform*  
*Developed by Anjana Urulugastenna | anjanau.com*  
*© 2025 All rights reserved*
"""
                    
                    st.download_button(
                        "💾 Download Chat History",
                        chat_text,
                        f"chat_history_{st.session_state.video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        "text/markdown",
                        help="Download complete chat history"
                    )

def render_analysis_results(analysis_data):
    """Render analysis results in a consistent format"""
    st.subheader("📝 Analysis Results")
    
    # Tabs for different results
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🎯 Topics", "❓ Questions", "😊 Sentiment"])
    
    with tab1:
        st.write("**Summary:**")
        st.write(analysis_data.get("summary", "No summary available"))
    
    with tab2:
        if analysis_data.get("topics"):
            st.write("**Key Topics:**")
            st.write(analysis_data["topics"])
        else:
            st.info("Topics not included in analysis")
    
    with tab3:
        if analysis_data.get("questions"):
            st.write("**Suggested Questions:**")
            for i, question in enumerate(analysis_data["questions"], 1):
                if st.button(f"💬 {question}", key=f"q_{i}"):
                    # Add question to chat
                    st.session_state.pending_question = question
                    st.rerun()
        else:
            st.info("Questions not included in analysis")
    
    with tab4:
        if analysis_data.get("sentiment"):
            st.write("**Sentiment Analysis:**")
            st.write(analysis_data["sentiment"])
        else:
            st.info("Sentiment analysis not included")

if __name__ == "__main__":
    main()
