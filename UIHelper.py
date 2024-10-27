#Importing Libaries
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import  HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
googelAPIKey = os.getenv('GOOGEL_API_KEY')

def loadYouTubeVideo(url):
    try:
        loader = YoutubeLoader.from_youtube_url(url)
        transcript = loader.load()
        if not transcript:
            raise ValueError("No transcript found for the provided URL.")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 100)
        docs = text_splitter.split_documents(transcript)
        return docs
    except Exception as e:
        raise RecursionError(f"Failed to load or process YouTube video: {str(e)}")

def embedingFunction():
    try:
        embedingFunctions = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return embedingFunctions
    except Exception as e:
        raise ValueError(f"Failed to load embedding function: {str(e)}")

def create_vector_store(docs, embedingFunctions):
    try:
        db = FAISS.from_documents(docs, embedingFunctions)
        return db
    except Exception as e:
        raise ValueError(f"Failed to create vector store: {str(e)}")

def sumarizeWithGemini(docs):
    try:
        combined_doc = " "
        for doc in docs:
            combined_doc += " " + doc.page_content
        
        template = f"""
            "Summarize the key points and main ideas from the following YouTube video transcript: {combined_doc}.
            Focus only on factual information and keep the summary concise and informative.
            **Important:** 
                * Focus on the key points and main ideas.
                * Keep the summary concise and informative.
                * Use factual information from the transcript only.
                # Add specific points extracted from the transcript
                    "** Key fact 1 from transcript...",
                    "** Key fact 2 from transcript...",
            # ...
                    """
        genai.configure(api_key=googelAPIKey)
        model = genai.GenerativeModel(model_name="gemini-pro")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        results = response.text
        results = results.replace("\n", "")
        return results
    except Exception as e:
        raise ValueError(f"Failed to summarize the video: {str(e)}")

def getrelventDataFromDB(db, query):
    try:
        results = db.similarity_search(query, k= 12)
        query_result = results[0].page_content
        return query_result
    except Exception as e:
        raise ValueError(f"Failed to get relevant data from the database: {str(e)}")

def optimizing_question(relative_contents, query):
    try:
        template = f"""
        You are a helpful and informative bot that answers questions using text from the reference context included below. 
        Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. 
        However, you are talking to a non-technical audience, so be sure to break down complicated concepts and 
        strike a friendly and conversational tone. 
        If the context is irrelevant to the answer, you may ignore it.
        
        QUESTION: '{query}'
        CONTEXT: '{relative_contents}'
        
        ANSWER:
            """
        genai.configure(api_key=googelAPIKey)
        model = genai.GenerativeModel(model_name="gemini-pro")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        results = response.text
        return results
    except Exception as e:
        raise ValueError(f"Failed to optimize the question: {str(e)}")

def display_summary(summary):
    try:
        points = summary.split("**")
        points = [point.strip() for point in points if point.strip()]
        return points
    except Exception as e:
        raise ValueError(f"Failed to display the summary: {str(e)}")
    
def optimizing_question_with_external_info(relative_contents, query):
    try:
        template = f"""
        You are a helpful and informative bot that answers questions primarily using information from outside the reference context, 
        while still considering and incorporating relevant details from the context when appropriate.
        Be sure to respond in a complete sentence, being comprehensive and offering relevant external information as much as possible.
        You are talking to a non-technical audience, so break down complicated concepts and strike a friendly and conversational tone.
        If the context is irrelevant to the answer, you may choose to not include it.
        
        QUESTION: '{query}'
        CONTEXT: '{relative_contents}'
        
        ANSWER:
            """
        genai.configure(api_key=googelAPIKey)
        model = genai.GenerativeModel(model_name="gemini-pro")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        results = response.text
        return results
    except Exception as e:
        raise ValueError(f"Failed to optimize the question: {str(e)}")