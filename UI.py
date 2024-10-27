import UIHelper as helper
import streamlit as st
import textwrap

st.set_page_config(layout="wide")
st.title("YouTube Video Assistant")
st.subheader("Powered by Googel Gemini")

if 'docs' not in st.session_state:
    st.session_state.docs = []
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'summary_points' not in st.session_state:
    st.session_state.summary_points = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'db' not in st.session_state:
    st.session_state.db = None

def process_video(url):
    try:
        with st.spinner("Analyzing video..."):
            st.session_state.docs = helper.loadYouTubeVideo(url)
            st.session_state.summary = helper.sumarizeWithGemini(st.session_state.docs)
            st.session_state.summary_points = helper.display_summary(st.session_state.summary)
            embedding_function = helper.embedingFunction()
            st.session_state.db = helper.create_vector_store(st.session_state.docs, embedding_function)
        st.success("Video analyzed successfully!")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Video Input")
    youtube_url = st.text_input("Enter YouTube video URL:")
    if st.button("Analyze New Video"):
        st.session_state.chat_history = []  # Clear chat history for new video
        process_video(youtube_url)

    if st.session_state.summary:
        with st.expander("Video Summary", expanded=False):
            st.subheader("Key Points")
            for point in st.session_state.summary_points:
                if "Key fact" in point:
                    st.markdown(f"- {point}")
                else:
                    st.markdown(f"**{point}**")

with col2:
    st.subheader("Chat with the Video Assistant")
    
    if not st.session_state.docs:
        st.info("Please enter a YouTube URL and click 'Analyze New Video' to start.")
    else:
        st.write("Ask multiple questions about the video. The assistant will remember the context.")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        question = st.chat_input("Ask a question about the video")
        use_external_source = st.checkbox("Use External Source")
        
        if question:
            try:
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.write(question)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        relevant_contents = helper.getrelventDataFromDB(st.session_state.db, question)
                        if use_external_source:
                            answer = helper.optimizing_question_with_external_info(relevant_contents, question)
                        else:
                            answer = helper.optimizing_question(relevant_contents, question)
                    
                    st.write(textwrap.fill(answer, width=80))
            
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            #st.experimental_rerun() 
            
st.markdown("<br><hr><p style='text-align: center;'>Developed by Anjana Urulugastenna @ 2024</p>", unsafe_allow_html=True)
