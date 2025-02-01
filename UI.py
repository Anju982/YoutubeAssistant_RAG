import streamlit as st
from typing import List, Optional
from dataclasses import dataclass, field
import textwrap
from functools import lru_cache
import UIHelper as helper

# Constants
PAGE_TITLE = "YouTube Video Assistant"
PAGE_ICON = "🎥"
PAGE_LAYOUT = "wide"

@dataclass
class SessionState:
    """Dataclass to manage application state."""
    docs: List = field(default_factory=list)
    summary: str = ""
    summary_points: List[str] = field(default_factory=list)
    chat_history: List[dict] = field(default_factory=list)
    db: Optional[object] = None
    video_url: str = ""

    def clear_chat(self) -> None:
        """Clear chat history."""
        self.chat_history = []

class YouTubeAssistant:
    """Main application class for YouTube Video Assistant."""
    
    def __init__(self):
        """Initialize the application."""
        self._setup_page()
        self._initialize_state()
        
    @staticmethod
    def _setup_page() -> None:
        """Configure page settings."""
        st.set_page_config(
            layout=PAGE_LAYOUT,
            page_title=PAGE_TITLE,
            page_icon=PAGE_ICON
        )
        st.title(PAGE_TITLE)
        st.subheader("Powered by Google Gemini")

    @staticmethod
    def _initialize_state() -> None:
        """Initialize session state if not exists."""
        if 'state' not in st.session_state:
            st.session_state.state = SessionState()

    @staticmethod
    @lru_cache(maxsize=100)
    def _get_youtube_video_id(url: str) -> str:
        """Extract YouTube video ID from URL with caching."""
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return ""

    def _embed_youtube_video(self, url: str) -> None:
        """Embed YouTube video player."""
        video_id = self._get_youtube_video_id(url)
        if video_id:
            st.video(f"https://youtu.be/{video_id}")

    def _process_video(self, url: str) -> None:
        """Process YouTube video URL and update state."""
        try:
            with st.spinner("Analyzing video..."):
                state = st.session_state.state
                state.video_url = url
                state.docs = helper.loadYouTubeVideo(url)
                state.summary = helper.sumarizeWithGemini(state.docs)
                state.summary_points = helper.display_summary(state.summary)
                state.db = helper.create_vector_store(
                    state.docs, 
                    helper.embedingFunction()
                )
            st.success("Video analyzed successfully!")
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")

    def _render_video_section(self) -> None:
        """Render video input section with controls."""
        state = st.session_state.state
        
        with st.container():
            st.subheader("Video Input")
            youtube_url = st.text_input(
                "Enter YouTube video URL:",
                key="youtube_url",
                placeholder="https://www.youtube.com/watch?v=..."
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Analyze New Video", help="Analyze the video and generate a summary"):
                    state.clear_chat()
                    self._process_video(youtube_url)
            
            with col2:
                if st.button("Play Video", help="Embed and play the video"):
                    if youtube_url:
                        self._embed_youtube_video(youtube_url)
                    else:
                        st.warning("Please enter a YouTube URL first")
            
            if state.video_url:
                with st.expander("Video Player", expanded=True):
                    self._embed_youtube_video(state.video_url)

    def _display_summary(self) -> None:
        """Display video summary in expandable section."""
        state = st.session_state.state
        if state.summary:
            with st.expander("Video Summary", expanded=False):
                st.subheader("Key Points")
                for point in state.summary_points:
                    st.markdown(f"- {point}")

    def _handle_chat(self, question: str, use_external_source: bool) -> None:
        """Process chat interactions."""
        state = st.session_state.state
        try:
            state.chat_history.append({"role": "user", "content": question})
            
            relevant_contents = helper.getrelventDataFromDB(state.db, question)
            answer = (
                helper.optimizing_question_with_external_info(relevant_contents, question)
                if use_external_source else
                helper.optimizing_question(relevant_contents, question)
            )
            
            state.chat_history.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Chat error: {str(e)}")

    def _render_chat_interface(self) -> None:
        """Render chat interface with history and input."""
        state = st.session_state.state
        
        st.subheader("Chat with the Video Assistant")
        
        if not state.docs:
            st.info("Please enter a YouTube URL and click 'Analyze New Video' to start.")
            return

        with st.container():
            st.write("Ask multiple questions about the video. The assistant will remember the context.")
            
            # Chat history
            for message in state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(textwrap.fill(message["content"], width=80))
            
            # Chat controls
            col1, col2 = st.columns([1, 4])
            with col1:
                use_external_source = st.checkbox(
                    "Use External Source",
                    key="external_source",
                    help="Include external data sources in the response"
                )
            
            with col2:
                question = st.chat_input(
                    "Ask a question about the video",
                    key=f"chat_input_{len(state.chat_history)}"
                )
                
                if question:
                    self._handle_chat(question, use_external_source)
                    st.rerun()
            
            if st.button("Clear Chat History", key="clear_chat", help="Clear the chat history"):
                state.clear_chat()
                st.rerun()

    @staticmethod
    def _render_footer() -> None:
        """Render application footer."""
        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown("""
                **Contact Information**  
                Website: [anjanau.com](https://anjanau.com)  
                Email: contact@anjanau.com
            """)
        
        with cols[1]:
            st.markdown("""
                **Additional Resources**
                - [Documentation](https://anjanau.com/docs)
                - [API Reference](https://anjanau.com/api)
                - [Support](https://anjanau.com/support)
            """)
        
        with cols[2]:
            st.markdown("""
                **About**  
                Developed by [Anjana Urulugastenna](https://anjanau.com/about)  
                © 2024 All rights reserved
            """)

    def run(self) -> None:
        """Run the application."""
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_video_section()
            self._display_summary()
        
        with col2:
            self._render_chat_interface()
        
        self._render_footer()

def main():
    """Application entry point."""
    app = YouTubeAssistant()
    app.run()

if __name__ == "__main__":
    main()