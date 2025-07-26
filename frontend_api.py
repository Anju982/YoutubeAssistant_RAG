"""
Streamlit Frontend for FastAPI Backend
This demonstrates how to use the FastAPI backend with a Streamlit frontend
"""

import streamlit as st
import requests
import time
from typing import Dict, Any

# FastAPI backend URL (adjust as needed)
API_BASE_URL = "http://localhost:8001"

# Page configuration
st.set_page_config(
    page_title="🎥 YouTube Assistant (API Version)",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.api-status {
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.5rem 0;
}
.status-healthy { background-color: #d4edda; color: #155724; }
.status-processing { background-color: #fff3cd; color: #856404; }
.status-error { background-color: #f8d7da; color: #721c24; }
.chat-message { 
    padding: 1rem; 
    margin: 0.5rem 0; 
    border-radius: 10px; 
    border-left: 4px solid #007bff;
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

def main():
    st.title("🎥 YouTube Assistant (API Version)")
    st.markdown("*Powered by FastAPI Backend + Streamlit Frontend*")
    
    # Check API health
    if not check_api_health():
        st.error("❌ FastAPI backend is not running! Please start it with: `uvicorn api:app --reload`")
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
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🎯 Analysis Settings")
        
        summary_type = st.selectbox(
            "Summary Type",
            ["comprehensive", "executive", "bullet_points", "key_topics"]
        )
        
        st.subheader("📊 Additional Features")
        include_sentiment = st.checkbox("Sentiment Analysis", value=False)
        include_topics = st.checkbox("Key Topics", value=True)
        include_questions = st.checkbox("Suggested Questions", value=True)
        
        external_sources = st.checkbox("Use External Sources in Chat", value=False)
        
        st.subheader("🔧 API Status")
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        # Show processed videos
        try:
            videos_response = requests.get(f"{API_BASE_URL}/api/v1/videos")
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                st.write(f"📊 Processed Videos: {videos_data['total']}")
        except Exception:
            st.write("📊 Could not fetch video count")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🎬 Video Analysis")
        
        # Video input
        video_url = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )
        
        if st.button("🚀 Analyze Video", type="primary"):
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
        
        # Status monitoring
        if st.session_state.video_id:
            st.subheader("📊 Analysis Status")
            
            try:
                status_data = get_analysis_status(st.session_state.video_id)
                
                if status_data["status"] == "completed":
                    st.markdown('<div class="api-status status-healthy">✅ Analysis Complete</div>', unsafe_allow_html=True)
                    
                    # Get analysis results
                    if st.button("📖 Load Results"):
                        try:
                            analysis_data = get_analysis_results(st.session_state.video_id, summary_type)
                            st.session_state.analysis_data = analysis_data
                            st.success("✅ Results loaded!")
                        except requests.exceptions.HTTPError as e:
                            if e.response.status_code == 202:
                                st.warning("⏳ Analysis still processing...")
                            else:
                                st.error(f"❌ Error loading results: {e}")
                        
                elif status_data["status"] == "processing":
                    st.markdown('<div class="api-status status-processing">⏳ Processing...</div>', unsafe_allow_html=True)
                    if st.button("🔄 Refresh Status"):
                        st.rerun()
                        
                elif status_data["status"] == "error":
                    st.markdown('<div class="api-status status-error">❌ Processing Error</div>', unsafe_allow_html=True)
                    st.error(f"Error: {status_data.get('error', 'Unknown error')}")
                
                # Show metadata
                if status_data.get("metadata"):
                    metadata = status_data["metadata"]
                    st.write("**Video Info:**")
                    st.write(f"- Title: {metadata.get('title', 'Unknown')}")
                    st.write(f"- Channel: {metadata.get('author_name', 'Unknown')}")
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Could not get status: {e}")
        
        # Display analysis results
        if st.session_state.analysis_data:
            st.subheader("📝 Analysis Results")
            
            data = st.session_state.analysis_data
            
            # Tabs for different results
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🎯 Topics", "❓ Questions", "😊 Sentiment"])
            
            with tab1:
                st.write("**Summary:**")
                st.write(data.get("summary", "No summary available"))
            
            with tab2:
                if data.get("topics"):
                    st.write("**Key Topics:**")
                    st.write(data["topics"])
                else:
                    st.info("Topics not included in analysis")
            
            with tab3:
                if data.get("questions"):
                    st.write("**Suggested Questions:**")
                    for i, question in enumerate(data["questions"], 1):
                        if st.button(f"💬 {question}", key=f"q_{i}"):
                            # Add question to chat
                            st.session_state.pending_question = question
                            st.rerun()
                else:
                    st.info("Questions not included in analysis")
            
            with tab4:
                if data.get("sentiment"):
                    st.write("**Sentiment Analysis:**")
                    st.write(data["sentiment"])
                else:
                    st.info("Sentiment analysis not included")
    
    with col2:
        st.header("💬 Chat with Video")
        
        if not st.session_state.video_id:
            st.info("👆 Please analyze a video first to start chatting!")
        else:
            # Chat interface
            chat_container = st.container()
            
            # Display chat history
            with chat_container:
                for chat in st.session_state.chat_history:
                    st.chat_message("user").write(chat["user"])
                    st.chat_message("assistant").write(chat["assistant"])
            
            # Chat input
            user_message = st.chat_input("Ask anything about the video...")
            
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
                    with st.spinner("🤔 Thinking..."):
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
            
            # Chat controls
            if st.session_state.chat_history:
                col_clear, col_export = st.columns(2)
                
                with col_clear:
                    if st.button("🗑️ Clear Chat"):
                        st.session_state.chat_history = []
                        st.rerun()
                
                with col_export:
                    if st.button("📥 Export Chat"):
                        chat_text = ""
                        for chat in st.session_state.chat_history:
                            chat_text += f"**You:** {chat['user']}\n\n"
                            chat_text += f"**Assistant:** {chat['assistant']}\n\n---\n\n"
                        
                        st.download_button(
                            "💾 Download Chat History",
                            chat_text,
                            f"chat_history_{st.session_state.video_id}.md",
                            "text/markdown"
                        )
    
    # Footer
    st.markdown("---")
    st.markdown("**🚀 YouTube Assistant API Version** | FastAPI Backend + Streamlit Frontend")

if __name__ == "__main__":
    main()
