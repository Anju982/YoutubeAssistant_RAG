# YouTube Video Assistant

Welcome to the **YouTube Video Assistant**! This application allows you to analyze YouTube videos, summarize the content, and engage in a question-and-answer dialogue about the video. The app uses various tools and technologies such as Streamlit, FAISS, Google Gemini, and Hugging Face Embeddings to provide a seamless and interactive experience.

## Features

- **YouTube Video Transcript Extraction**: Retrieve transcripts from YouTube videos using `YoutubeLoader`.
- **Summarization with Google Gemini**: Summarize key points and main ideas from the video.
- **Interactive Chat**: Ask questions about the video, and the assistant provides responses using context from the transcript.
- **Optional External Sourcing**: Toggle to use external sources for more comprehensive answers.
- **Vector Similarity Search**: Uses FAISS to fetch relevant video segments for better contextual responses.

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
