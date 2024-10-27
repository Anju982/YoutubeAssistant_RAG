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
```
## Installation

### Clone this repository:
```plaintext
git clone https://github.com/yourusername/youtube-video-assistant.git
cd youtube-video-assistant
```

### Install dependencies:
```plaintext
pip install -r requirements.txt
```

### Run the app:

```plaintext
streamlit run app.py
```

### Access the application at http://localhost:8501 in your browser.

## Usage

- Enter a YouTube video URL and click Analyze New Video to retrieve and summarize the video transcript.
- View the summary or engage in a chat with the assistant.
- Use the Use External Source checkbox to toggle between using only the video transcript or incorporating external information.
- Clear chat history as needed and start a new analysis if desired.

## Repository Structure

- app.py: The main application code for Streamlit interface and user interaction.
- helper.py: Contains helper functions for loading transcripts, summarizing content, and generating responses.
- .env: Environment file for storing API keys securely.

## License

- This project is licensed under the MIT License. Feel free to modify and distribute as needed.

Developed by Anjana Urulugastenna @ 2024
