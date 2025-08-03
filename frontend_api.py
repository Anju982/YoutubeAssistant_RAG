"""
Streamlit Frontend for FastAPI Backend
This demonstrates how to use the FastAPI backend with a Streamlit frontend
"""

import streamlit as st
import requests
import time
import os
import socket
from typing import Dict, Any, List
from datetime import datetime

# Dynamic FastAPI backend URL configuration
def get_api_base_url():
    """Get the appropriate API base URL based on environment"""
    # Check if running in network mode (environment variable)
    if os.getenv('FASTAPI_HOST'):
        return f"http://{os.getenv('FASTAPI_HOST')}:{os.getenv('FASTAPI_PORT', '8001')}"
    
    # Try to detect current host from Streamlit
    try:
        # Get the current URL from Streamlit (if available)
        if hasattr(st, '_get_websocket_headers'):
            headers = st._get_websocket_headers()
            if headers and 'host' in headers:
                host = headers['host'].split(':')[0]
                return f"http://{host}:8001"
    except:
        pass
    
    # Check if we can access localhost
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            return "http://localhost:8001"
    except:
        pass
    
    # Try common network configurations
    import socket
    try:
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Test if FastAPI is running on local IP
        test_response = requests.get(f"http://{local_ip}:8001/health", timeout=2)
        if test_response.status_code == 200:
            return f"http://{local_ip}:8001"
    except:
        pass
    
    # Default fallback
    return "http://localhost:8001"

# Initialize API base URL
API_BASE_URL = get_api_base_url()

# Page configuration
st.set_page_config(
    page_title="🎥 YouTube Assistant - AI Video Analysis Platform",
    page_icon="🎥", 
    layout="wide",
    initial_sidebar_state="collapsed",
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

/* Sidebar Styling - HIDE SIDEBAR COMPLETELY */
.css-1d391kg, [data-testid="stSidebar"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
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

/* Modern Professional Footer Styling */
.modern-footer {
    background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%);
    color: #e2e8f0;
    margin-top: 3rem;
    position: relative;
    overflow: hidden;
}

.modern-footer::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4c72c4 0%, #667eea 50%, #4c72c4 100%);
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem 2rem 1.5rem 2rem;
}

.footer-top {
    display: grid;
    grid-template-columns: 2.5fr 1fr 1fr 1fr;
    gap: 3rem;
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #2d3748;
}

.footer-brand-section {
    max-width: 400px;
}

.brand-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.brand-title h2 {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #4c72c4 0%, #667eea 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.brand-description {
    color: #a0aec0;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

.brand-highlights {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.highlight-tag {
    background: rgba(76, 114, 196, 0.15);
    color: #90cdf4;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    border: 1px solid rgba(76, 114, 196, 0.3);
}

.footer-section {
    min-width: 0;
}

.footer-section h3 {
    color: #f7fafc;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    position: relative;
    padding-bottom: 0.5rem;
}

.footer-section h3::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 40px;
    height: 2px;
    background: linear-gradient(90deg, #4c72c4, #667eea);
    border-radius: 1px;
}

.footer-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.footer-list li {
    margin-bottom: 0.6rem;
}

.footer-list a {
    color: #a0aec0;
    text-decoration: none;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    display: inline-block;
    position: relative;
}

.footer-list a:hover {
    color: #90cdf4;
    transform: translateX(4px);
}

.footer-list a::before {
    content: '→';
    position: absolute;
    left: -20px;
    opacity: 0;
    transition: opacity 0.3s ease;
    color: #4c72c4;
}

.footer-list a:hover::before {
    opacity: 1;
}

.tech-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.4rem 0;
    color: #a0aec0;
    font-size: 0.85rem;
}

.tech-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(76, 114, 196, 0.2);
    border-radius: 4px;
    font-size: 0.7rem;
}

.developer-card {
    background: linear-gradient(135deg, rgba(76, 114, 196, 0.1) 0%, rgba(102, 126, 234, 0.1) 100%);
    padding: 1.2rem;
    border-radius: 12px;
    border: 1px solid rgba(76, 114, 196, 0.2);
    margin-bottom: 1rem;
}

.developer-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f7fafc;
    margin-bottom: 0.3rem;
}

.developer-title {
    color: #90cdf4;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
    font-weight: 500;
}

.developer-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #4c72c4;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.developer-link:hover {
    color: #667eea;
    transform: translateY(-1px);
}

.footer-bottom {
    padding: 1.5rem 0;
    border-top: 1px solid #2d3748;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.copyright-text {
    color: #718096;
    font-size: 0.85rem;
    margin: 0;
}

.footer-social {
    display: flex;
    gap: 0.8rem;
}

.social-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(76, 114, 196, 0.1);
    color: #90cdf4;
    text-decoration: none;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid rgba(76, 114, 196, 0.2);
    transition: all 0.3s ease;
}

.social-btn:hover {
    background: rgba(76, 114, 196, 0.2);
    color: #f7fafc;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(76, 114, 196, 0.3);
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .footer-top {
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
    }
    
    .footer-brand-section {
        max-width: 100%;
    }
}

@media (max-width: 768px) {
    .footer-content {
        padding: 2rem 1rem 1rem 1rem;
    }
    
    .footer-top {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .footer-bottom {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
    
    .footer-social {
        justify-content: center;
    }
    
    .brand-highlights {
        justify-content: center;
    }
}

/* Hide old footer styles */
.professional-footer,
.footer-card,
.copyright-card {
    display: none !important;
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

/* Select Box Dropdown Styling - Fix overlay issue */
.stSelectbox > div > div > div > div {
    background: #34495e !important;
    color: #e0e0e0 !important;
    border: 2px solid #3d4a6a !important;
    z-index: 9999 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
}

/* Select Box Options */
.stSelectbox [role="listbox"] {
    background: #34495e !important;
    border: 2px solid #3d4a6a !important;
    z-index: 9999 !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important;
    max-height: 200px !important;
    overflow-y: auto !important;
}

.stSelectbox [role="option"] {
    background: #34495e !important;
    color: #e0e0e0 !important;
    padding: 0.5rem 1rem !important;
}

.stSelectbox [role="option"]:hover {
    background: #4c72c4 !important;
    color: #f0f2f5 !important;
}

.stSelectbox [aria-selected="true"] {
    background: #4c72c4 !important;
    color: #f0f2f5 !important;
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
    margin-left: 0 !important;
    width: 100% !important;
}

/* Header area */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* All containers */
.stContainer, .block-container {
    background: transparent !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Columns */
[data-testid="column"] {
    background: transparent !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Main content area optimized for full width */
.main .block-container {
    position: relative !important;
    z-index: 1 !important;
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
    """Check if FastAPI backend is running with enhanced error handling"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        # Try alternative health endpoints
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=3)
            return response.status_code in [200, 404]  # 404 is OK, means server is running
        except:
            return False
    except requests.exceptions.Timeout:
        return False
    except Exception:
        return False

def get_api_status_info() -> Dict[str, Any]:
    """Get detailed API status information"""
    status_info = {
        "api_url": API_BASE_URL,
        "reachable": False,
        "response_time": None,
        "error": None
    }
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        status_info["response_time"] = round(time.time() - start_time, 2)
        
        if response.status_code == 200:
            status_info["reachable"] = True
            try:
                status_info["backend_info"] = response.json()
            except:
                status_info["backend_info"] = {"message": "Backend responding"}
        else:
            status_info["error"] = f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        status_info["error"] = "Connection refused - Backend not running or wrong URL"
    except requests.exceptions.Timeout:
        status_info["error"] = "Connection timeout - Backend too slow or network issues"
    except Exception as e:
        status_info["error"] = str(e)
    
    return status_info

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
    # Declare global variable at the beginning
    global API_BASE_URL
    
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
    
    # Move former sidebar content to main area - API Configuration Section
    st.markdown("### ⚙️ Configuration & Settings")
    
    # Create columns for the configuration section
    config_col1, config_col2, config_col3, config_col4 = st.columns([1, 1, 1, 1])
    
    with config_col1:
        # API status indicator
        api_health = check_api_health()
        status_color = "#4c72c4" if api_health else "#e74c3c"
        status_text = "✅ Connected" if api_health else "❌ Disconnected"
        
        st.markdown(f"""
        <div style="background: {status_color}; color: white; padding: 0.5rem; 
                    border-radius: 8px; text-align: center; margin-bottom: 1rem; font-size: 0.9rem;">
            <strong>{status_text}</strong><br>API: {API_BASE_URL.split('://')[1] if '://' in API_BASE_URL else API_BASE_URL}
        </div>
        """, unsafe_allow_html=True)
    
    with config_col2:
        # Summary type selection
        summary_type = st.selectbox(
            "📝 Summary Type",
            ["comprehensive", "executive", "bullet_points", "key_topics"],
            help="Select the type of summary you want",
            key="summary_type"
        )
    
    with config_col3:
        # Quick status indicator
        try:
            videos_response = requests.get(f"{API_BASE_URL}/api/v1/videos", timeout=1)
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                st.metric("📊 Videos Analyzed", videos_data['total'])
            else:
                st.metric("📊 Videos Analyzed", "N/A")
        except Exception:
            st.metric("📊 Videos Analyzed", "N/A")
    
    with config_col4:
        # Quick refresh button
        if st.button("🔄 Refresh Status", help="Refresh API status and metrics"):
            st.rerun()
    
    # Analysis features section
    st.markdown("**📊 Analysis Features**")
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns([1, 1, 1, 1])
    
    with feature_col1:
        include_sentiment = st.checkbox("😊 Sentiment Analysis", value=False, help="Analyze emotional tone", key="include_sentiment")
    
    with feature_col2:
        include_topics = st.checkbox("🎯 Topic Extraction", value=True, help="Extract key themes", key="include_topics")
    
    with feature_col3:
        include_questions = st.checkbox("❓ Generate Questions", value=True, help="Generate suggested questions", key="include_questions")
    
    with feature_col4:
        # API Configuration in expandable section
        with st.expander("🔧 API Configuration", expanded=False):
            st.markdown(f"**Current API URL:** `{API_BASE_URL}`")
            
            custom_api_url = st.text_input(
                "Custom API URL:",
                placeholder="http://server-ip:8001",
                help="Enter custom FastAPI URL if needed"
            )
            
            if custom_api_url and custom_api_url != API_BASE_URL:
                if st.button("🔄 Update API URL"):
                    API_BASE_URL = custom_api_url.rstrip('/')
                    st.rerun()
            
            if st.button("🔍 Test Connection"):
                with st.spinner("Testing connection..."):
                    health_status = check_api_health()
                    if health_status:
                        st.success("✅ API is responsive")
                    else:
                        st.error("❌ Cannot connect to API")
                        st.info("💡 For network access: `uvicorn api:app --host 0.0.0.0 --port 8001`")
        
        # Gemini Model Management Section
        with st.expander("🤖 Gemini Model Configuration", expanded=False):
            try:
                # Get current model info
                model_response = requests.get(f"{API_BASE_URL}/api/v1/models", timeout=5)
                if model_response.status_code == 200:
                    model_info = model_response.json()
                    
                    # Display current model
                    current_model = model_info["current_model"]
                    st.markdown(f"**Current Model:** {current_model['display_name']}")
                    st.caption(current_model["description"])
                    
                    # Model selection
                    available_models = model_info["available_models"]
                    model_options = {model["display_name"]: model["name"] for model in available_models}
                    
                    selected_display_name = st.selectbox(
                        "Select Gemini Model:",
                        options=list(model_options.keys()),
                        index=list(model_options.values()).index(current_model["name"]),
                        help="Choose which Gemini model to use for analysis"
                    )
                    
                    selected_model_name = model_options[selected_display_name]
                    
                    # Show model details
                    selected_model_info = next(m for m in available_models if m["name"] == selected_model_name)
                    st.info(f"**{selected_model_info['display_name']}:** {selected_model_info['description']}")
                    
                    # Switch model button
                    if selected_model_name != current_model["name"]:
                        if st.button(f"🔄 Switch to {selected_display_name}", type="primary"):
                            try:
                                switch_response = requests.post(
                                    f"{API_BASE_URL}/api/v1/models/switch",
                                    json={"model_name": selected_model_name},
                                    timeout=5
                                )
                                if switch_response.status_code == 200:
                                    st.success(f"✅ Successfully switched to {selected_display_name}")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to switch model: {switch_response.text}")
                            except requests.exceptions.RequestException as e:
                                st.error(f"❌ Error switching model: {str(e)}")
                    
                    # Display fallback models
                    if model_info.get("fallback_models"):
                        st.markdown("**Fallback Models:**")
                        for fallback in model_info["fallback_models"]:
                            st.caption(f"• {fallback['display_name']}")
                    
                else:
                    st.warning("⚠️ Could not load model information")
                    
            except requests.exceptions.RequestException:
                st.warning("⚠️ Model management requires API connection")
    
    
    # Add separator
    st.markdown("---")
    
    # Check API health with enhanced error handling
    api_status = check_api_health()
    if not api_status:
        st.error(f"❌ FastAPI backend is not accessible at: `{API_BASE_URL}`")
        
        # Provide helpful suggestions
        st.markdown("""
        ### 🔧 Backend Connection Issues
        
        **If accessing from a different device:**
        1. **Start FastAPI for network access:**
           ```bash
           uvicorn api:app --host 0.0.0.0 --port 8001
           ```
        
        2. **Update the API URL in the configuration section** to use your server's IP address:
           - Example: `http://192.168.1.100:8001`
           - Replace `192.168.1.100` with your actual server IP
        
        3. **Check firewall settings** - ensure port 8001 is open
        
        **If running locally:**
        - Start the backend with: `./start.sh backend` or `python api.py`
        
        **Current API URL:** `{API_BASE_URL}`
        """)
        
        # Don't stop the app, allow users to configure API URL
        st.warning("⚠️ Some features may not work without backend connection")
    else:
        st.success(f"✅ Connected to FastAPI backend at: `{API_BASE_URL}`")
        
        # Add rate limit information banner
        with st.expander("ℹ️ About API Rate Limits & Model Information", expanded=False):
            # Get current model info if available
            try:
                model_response = requests.get(f"{API_BASE_URL}/api/v1/models", timeout=2)
                if model_response.status_code == 200:
                    model_info = model_response.json()
                    current_model = model_info["current_model"]
                    st.success(f"**Current AI Model:** {current_model['display_name']}")
                    st.caption(current_model["description"])
                else:
                    st.info("**Current AI Model:** Gemini 2.0 Flash-Lite (default)")
            except:
                st.info("**Current AI Model:** Gemini 2.0 Flash-Lite (default)")
            
            st.info("""
            **Gemini API Usage Information:**
            
            This application uses Google's Gemini API for AI analysis. Features include:
            
            • **Multiple Model Support:** Gemini 2.0 Flash-Lite, 2.0 Flash, 1.5 Flash, and future models
            • **Automatic Fallback:** If primary model hits limits, automatically tries fallback models
            • **Rate Limit Handling:** Intelligent retry with exponential backoff
            • **Graceful Degradation:** When limits are reached, core functionality remains available
            
            **If you hit rate limits:**
            • Video transcripts remain available for chat
            • Cached analysis results are preserved
            • System automatically tries alternative models
            • Full functionality returns when quota resets (usually 24 hours)
            • Consider upgrading to paid plan for higher limits
            
            **Rate limit friendly tips:**
            • Use cached results when available
            • Switch to different models if needed
            • Chat interface works with existing analyzed content
            • Model switching available in configuration
            """)
    
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
    
    # Professional Footer - Pure Streamlit Components
    st.markdown("---")
    
    # Footer content using pure Streamlit components
    st.markdown("### 🎥 YouTube Assistant Platform")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("**About the Platform**")
        st.write("Advanced AI-powered platform for YouTube video analysis, comparison, and insights. Transform how you understand video content with cutting-edge technology.")
        
        # Technology highlights
        st.markdown("**Key Technologies:**")
        tech_tags = ["🤖 AI Analysis", "⚖️ Video Comparison", "📈 Trend Detection", "🔗 RAG Technology"]
        st.write(" • ".join(tech_tags))
        
        # Developer info
        st.markdown("**Developer:**")
        st.write("**Anjana Urulugastenna** - Quantitative Analyst & AI Engineer")
        st.markdown("[🌐 Visit Portfolio](https://anjanau.com/)")
    
    with col2:
        st.markdown("**Platform Features**")
        features = [
            "🎬 Single Video Analysis",
            "⚖️ Multi-Video Comparison", 
            "📈 Trend Analysis",
            "💬 AI Chat Interface",
            "📊 Content Insights",
            "📈 Analytics Dashboard"
        ]
        for feature in features:
            st.write(f"• {feature}")
    
    with col3:
        st.markdown("**Technology Stack**")
        stack = [
            "🔧 **Backend:** FastAPI + Python",
            "🎨 **Frontend:** Streamlit", 
            "🤖 **AI:** Google Gemini",
            "🔗 **Framework:** LangChain",
            "📊 **Vector DB:** FAISS"
        ]
        for tech in stack:
            st.write(tech)
    
    with col4:
        st.markdown("**Resources**")
        resources = [
            "[Professional Portfolio](https://anjanau.com/)",
            "[Other Projects](https://anjanau.com/projects)",
            "[Research Work](https://anjanau.com/research)", 
            "[Contact](https://anjanau.com/contact)"
        ]
        for resource in resources:
            st.write(f"• {resource}")
    
    # Footer bottom
    st.markdown("---")
    
    footer_col1, footer_col2 = st.columns([2, 1])
    
    with footer_col1:
        st.caption("© 2025 Anjana Urulugastenna • YouTube Assistant Platform • All Rights Reserved")
    
    with footer_col2:
        st.markdown("""
        [🌐 Portfolio](https://anjanau.com/) | [📧 Contact](https://anjanau.com/contact)
        """)
    
    st.markdown("")  # Add some spacing

def render_single_video_tab():
    """Render the single video analysis tab"""
    # Get analysis settings from session state (set in configuration section)
    summary_type = st.session_state.get('summary_type', 'comprehensive')
    include_sentiment = st.session_state.get('include_sentiment', False)
    include_topics = st.session_state.get('include_topics', True)
    include_questions = st.session_state.get('include_questions', True)
    
    # Main content with professional styling
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎬 Video Analysis")
        st.write("Analyze any YouTube video with advanced AI-powered insights")
        
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
            st.subheader("📊 Analysis Status")
            
            try:
                status_data = get_analysis_status(st.session_state.video_id)
                
                if status_data["status"] == "completed":
                    st.success("✅ Analysis Complete")
                    
                    # Get analysis results with fallback logic
                    if st.button("📖 Load Results", help="Load comprehensive analysis results"):
                        # Try different summary types to find existing results
                        summary_types_to_try = [summary_type, "comprehensive", "executive", "bullet_points", "key_topics"]
                        analysis_loaded = False
                        
                        for st_type in summary_types_to_try:
                            try:
                                analysis_data = get_analysis_results(st.session_state.video_id, st_type)
                                st.session_state.analysis_data = analysis_data
                                if st_type != summary_type:
                                    st.info(f"✅ Results loaded with '{st_type}' summary type. You can re-analyze with '{summary_type}' if needed.")
                                else:
                                    st.success("✅ Results loaded successfully!")
                                analysis_loaded = True
                                break
                            except requests.exceptions.HTTPError as e:
                                if e.response.status_code == 404:
                                    continue  # Try next summary type
                                elif e.response.status_code == 202:
                                    st.warning("⏳ Analysis still processing...")
                                    analysis_loaded = True
                                    break
                                else:
                                    st.error(f"❌ Error loading results: {e}")
                                    analysis_loaded = True
                                    break
                        
                        if not analysis_loaded:
                            st.error("❌ No analysis results found. Please re-analyze the video.")
                            
                    # Option to re-analyze with different summary type
                    if st.button("🔄 Re-analyze with Current Settings", help="Re-analyze video with current summary type"):
                        video_url = f"https://www.youtube.com/watch?v={st.session_state.video_id}"
                        try:
                            with st.spinner("🎯 Re-analyzing video..."):
                                result = analyze_video_api(
                                    video_url, 
                                    summary_type, 
                                    include_sentiment, 
                                    include_topics, 
                                    include_questions
                                )
                                st.success("✅ Re-analysis started! Check status in a moment.")
                        except Exception as e:
                            st.error(f"❌ Error re-analyzing: {str(e)}")
                        
                elif status_data["status"] == "processing":
                    st.info("⏳ Processing...")
                    if st.button("🔄 Refresh Status", key="refresh_single"):
                        st.rerun()
                        
                elif status_data["status"] == "error":
                    st.error("❌ Processing Error")
                    st.error(f"Error: {status_data.get('error', 'Unknown error')}")
                
                # Show metadata with professional styling
                if status_data.get("metadata"):
                    metadata = status_data["metadata"]
                    st.subheader("📺 Video Information")
                    st.write(f"**Title:** {metadata.get('title', 'Unknown')}")
                    st.write(f"**Channel:** {metadata.get('author_name', 'Unknown')}")
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Could not get status: {e}")
        
        # Display analysis results with enhanced styling
        if st.session_state.analysis_data:
            render_analysis_results(st.session_state.analysis_data)

def render_comparison_tab():
    """Render the video comparison tab"""
    st.subheader("⚖️ Compare Multiple Videos")
    st.write("*Compare 2-10 videos on similar topics to identify differences, similarities, and unique insights powered by advanced AI analysis.*")
    
    # Video URLs input with professional styling
    st.subheader("📺 Videos to Compare")
    st.write("Add YouTube URLs for videos you want to compare (minimum 2, maximum 10)")
    
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
    st.subheader("⚙️ Comparison Settings")
    st.write("Configure how you want the videos to be compared")
    
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
        st.subheader("📊 Comparison Progress")
        
        try:
            comparison_data = get_comparison_results(st.session_state.comparison_id)
            
            if comparison_data["status"] == "completed":
                st.success("✅ Comparison completed!")
                st.session_state.comparison_data = comparison_data
                
                # Display results with enhanced styling
                if comparison_data.get("comparison_results"):
                    st.subheader("🔍 Comparison Results")
                    
                    # Videos analyzed
                    videos = comparison_data.get("videos", [])
                    st.subheader("📺 Analysis Summary")
                    st.write(f"**Videos Analyzed:** {len(videos)}")
                    
                    with st.expander("📺 Videos Overview", expanded=True):
                        for i, video in enumerate(videos, 1):
                            metadata = video.get("metadata", {})
                            st.write(f"**{i}. {metadata.get('title', 'Unknown Title')}**")
                            st.write(f"📺 Channel: {metadata.get('author_name', 'Unknown')}")
                            st.write(f"🔗 [View Video]({video.get('url', '#')})")
                    
                    # Comparison analysis
                    analysis = comparison_data["comparison_results"].get("comparison_analysis", "")
                    if analysis:
                        st.subheader("📋 Detailed Analysis")
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
                st.info(f"⏳ Processing... ({progress}/{total} videos analyzed)")
                
                if st.button("🔄 Refresh Progress", key="refresh_comparison"):
                    st.rerun()
                    
            elif comparison_data["status"] == "error":
                st.error(f"❌ Comparison failed: {comparison_data.get('error', 'Unknown error')}")
                
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
    st.subheader("💬 Chat with Analyzed Videos")
    st.write("Interactive Q&A with your analyzed video content using advanced RAG (Retrieval-Augmented Generation)")
    
    if not st.session_state.video_id:
        st.warning("🎬 No Videos Analyzed Yet")
        st.info("To start chatting, first analyze a video using one of these options:")
        st.write("📺 **Single Video Analysis** - Analyze individual videos")
        st.write("⚖️ **Compare Videos** - Compare multiple videos") 
        st.write("📈 **Trend Analysis** - Analyze video trends")
        st.write("*Once analysis is complete, return here to chat with the content!*")
    else:
        # Chat settings
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 **Chat Tips:** Ask about video content, request summaries, or explore topics in depth")
        
        with col2:
            external_sources = st.checkbox("🌐 External Sources", value=False, 
                                         help="Include external knowledge in responses")
        
        # Chat interface with professional styling
        chat_container = st.container()
        
        # Display chat history with enhanced styling
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                # User message
                with st.chat_message("user"):
                    st.write(chat["user"])
                
                # Assistant message
                with st.chat_message("assistant"):
                    st.write(chat["assistant"])
        
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
    """Render analysis results in a consistent format with rate limit awareness"""
    st.subheader("📝 Analysis Results")
    
    # Tabs for different results
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🎯 Topics", "❓ Questions", "😊 Sentiment"])
    
    with tab1:
        st.write("**Summary:**")
        summary_text = analysis_data.get("summary", "No summary available")
        
        # Check if summary contains rate limit message
        if "⚠️" in summary_text and ("rate limit" in summary_text.lower() or "quota" in summary_text.lower()):
            st.warning(summary_text)
            st.info("💡 **Chat is still available!** You can ask questions about the video content using the Chat Interface tab.")
        else:
            st.write(summary_text)
    
    with tab2:
        topics_text = analysis_data.get("topics")
        if topics_text:
            st.write("**Key Topics:**")
            # Check if topics contains rate limit message
            if "⚠️" in topics_text and ("rate limit" in topics_text.lower() or "quota" in topics_text.lower()):
                st.warning(topics_text)
            else:
                st.write(topics_text)
        else:
            st.info("Topics not included in analysis")
    
    with tab3:
        questions = analysis_data.get("questions")
        if questions:
            st.write("**Suggested Questions:**")
            # Handle both list and string format for questions
            if isinstance(questions, list):
                for i, question in enumerate(questions, 1):
                    if st.button(f"💬 {question}", key=f"q_{i}"):
                        # Add question to chat
                        st.session_state.pending_question = question
                        st.rerun()
            else:
                # String format (could be rate limit message)
                if "⚠️" in questions and ("rate limit" in questions.lower() or "quota" in questions.lower()):
                    st.warning(questions)
                else:
                    st.write(questions)
        else:
            st.info("Questions not included in analysis")
    
    with tab4:
        sentiment_text = analysis_data.get("sentiment")
        if sentiment_text:
            st.write("**Sentiment Analysis:**")
            # Check if sentiment contains rate limit message  
            if "⚠️" in sentiment_text and ("rate limit" in sentiment_text.lower() or "quota" in sentiment_text.lower()):
                st.warning(sentiment_text)
            else:
                st.write(sentiment_text)
        else:
            st.info("Sentiment analysis not included")

if __name__ == "__main__":
    main()
