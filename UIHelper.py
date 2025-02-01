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
                    Summarize the key points and main ideas from the following YouTube video transcript: {combined_doc}. Provide a comprehensive and informative summary, focusing on factual information from the transcript.

                    Specifically, address the following aspects:

                    * **Main Topic:** What is the central subject of the video?
                    * **Key Arguments/Points:**  What are the core arguments or points presented? Provide sufficient detail for each.
                    * **Supporting Evidence/Examples:** What evidence, examples, or data are used to support these arguments?
                    * **Important Details/Nuances:** Are there any crucial details, exceptions, or qualifications necessary for a complete understanding?
                    * **Overall Conclusion/Takeaway:** What is the main conclusion or takeaway message conveyed in the video?

                    **Instructions:**

                    * Use only factual information from the transcript. Do not add information from external sources or speculate.
                    * Be comprehensive. Aim for a detailed summary that captures the essence of the video, even if it means the summary is not extremely brief.  Prioritize information over brevity.
                    * Organize the summary logically and use clear, concise language.

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
                        You are a helpful and informative bot designed to answer questions based on the provided context.  Your goal is to provide comprehensive and easy-to-understand answers, even to non-technical audiences.

                        **Question:** '{query}'

                        **Context:** '{relative_contents}'

                        **Instructions:**

                        1. **Answer completely and comprehensively:**  Provide a full and detailed answer to the question, drawing upon all relevant information from the context.  Don't just give short, surface-level responses.

                        2. **Explain clearly and simply:**  Break down complex concepts into simpler terms that a non-technical audience can understand.  Use clear, concise language and avoid jargon or technical terms whenever possible.  Provide examples or analogies if they would be helpful.

                        3. **Maintain a friendly and conversational tone:**  Write your answer in a friendly and approachable way.  Use a conversational style as if you were explaining the topic to a friend.

                        4. **Use only the provided context:**  Base your answer *exclusively* on the information given in the context. Do not include information from other sources or speculate. If the context doesn't contain the information needed to answer the question, simply state, "The answer to this question cannot be found in the provided context."

                        5. **Structure your response logically:** Organize your answer in a clear and logical way, making it easy for the reader to follow your explanation.  Use headings, bullet points, or numbered lists if appropriate.

                        **Answer:**
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
                    You are a helpful and informative bot designed to answer questions using your general knowledge and external information, while also considering and integrating relevant details from the provided context.  Your goal is to provide comprehensive and easy-to-understand answers, even to non-technical audiences.

                    **Question:** '{query}'

                    **Context:** '{relative_contents}'

                    **Instructions:**

                    1. **Answer comprehensively using external knowledge:** Provide a full and detailed answer to the question, drawing primarily from your own knowledge base and external information.  Go beyond the context provided and offer additional relevant details.

                    2. **Integrate relevant context:**  Carefully review the provided context and incorporate any relevant information into your answer.  Explain how the context relates to the broader topic and how it supports or contrasts with your external knowledge.  If the context provides specific examples or details, be sure to include them.

                    3. **Explain clearly and simply:** Break down complex concepts into simpler terms that a non-technical audience can understand. Use clear, concise language and avoid jargon or technical terms whenever possible.  Provide examples or analogies if they would be helpful.

                    4. **Maintain a friendly and conversational tone:** Write your answer in a friendly and approachable way. Use a conversational style as if you were explaining the topic to a friend.

                    5. **Acknowledge the context:**  In your answer, explicitly acknowledge that you have considered the provided context.  For example, you could say, "While the context mentions [specific detail], it's important to also consider..." or "In addition to the information in the context, it's worth noting that..."

                    6. **Structure your response logically:** Organize your answer in a clear and logical way, making it easy for the reader to follow your explanation. Use headings, bullet points, or numbered lists if appropriate.

                    7. **Handle irrelevant context gracefully:** If the context is not relevant to the question, you can choose to not include it directly in your answer. However, you could still briefly acknowledge it by saying something like, "While the provided context touches on [topic], the main answer to your question is..."  Avoid simply ignoring the context entirely.

                    **Answer:**
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