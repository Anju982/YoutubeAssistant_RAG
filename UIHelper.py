#Importing Libaries
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import  HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
import os
import google.generativeai as genai
import re
import requests
import json
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid YouTube URL format")

def get_video_metadata(video_id):
    """Get video metadata including title, thumbnail, duration, and channel info."""
    try:
        # Use YouTube oEmbed API (no API key required)
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract metadata
            metadata = {
                'title': data.get('title', f'YouTube Video: {video_id}'),
                'author_name': data.get('author_name', 'Unknown Channel'),
                'author_url': data.get('author_url', ''),
                'thumbnail_url': data.get('thumbnail_url', ''),
                'width': data.get('width', 0),
                'height': data.get('height', 0),
                'provider_name': data.get('provider_name', 'YouTube'),
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
            return metadata
        else:
            # Fallback metadata if API call fails
            return {
                'title': f'YouTube Video: {video_id}',
                'author_name': 'Unknown Channel',
                'author_url': '',
                'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        # Return basic metadata on error
        return {
            'title': f'YouTube Video: {video_id}',
            'author_name': 'Unknown Channel',
            'author_url': '',
            'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'video_id': video_id,
            'video_url': f"https://www.youtube.com/watch?v={video_id}",
            'error': str(e)
        }

def loadYouTubeVideo(url):
    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)
        
        # Get video metadata
        metadata = get_video_metadata(video_id)
        
        # Create API instance
        api = YouTubeTranscriptApi()
        
        # Get transcript using the current API
        try:
            # Check if transcripts are available and get the list
            transcript_list = api.list(video_id)
        except TranscriptsDisabled:
            raise ValueError("Transcripts are disabled for this video.")
        except Exception as e:
            raise ValueError(f"Failed to get transcript list: {str(e)}")
        
        # Find English transcript or the first available one
        transcript_data = None
        transcript_language = "en"
        try:
            # Try to get English transcript first
            transcript = transcript_list.find_transcript(['en'])
            transcript_data = transcript.fetch()
        except NoTranscriptFound:
            try:
                # If no English, try to get the first available transcript
                for transcript in transcript_list:
                    transcript_data = transcript.fetch()
                    transcript_language = transcript.language_code
                    break
                if not transcript_data:
                    raise ValueError("No transcript found for this video.")
            except Exception as e:
                raise ValueError(f"No transcript available: {str(e)}")
        
        if not transcript_data:
            raise ValueError("No transcript data retrieved.")
        
        # Convert transcript to text with timestamps
        transcript_text = " ".join([snippet.text for snippet in transcript_data])
        
        # Enhanced metadata with transcript info
        enhanced_metadata = {
            **metadata,
            'source': url,
            'transcript_language': transcript_language,
            'transcript_length': len(transcript_data),
            'processed_at': datetime.now().isoformat()
        }
        
        # Create Document object with enhanced metadata
        documents = [Document(
            page_content=transcript_text,
            metadata=enhanced_metadata
        )]
        
        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)
        
        # Add metadata to all chunks
        for doc in docs:
            doc.metadata.update(enhanced_metadata)
        
        return docs, enhanced_metadata
        
    except Exception as e:
        raise Exception(f"Failed to load or process YouTube video: {str(e)}")

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

def sumarizeWithGemini(docs, summary_type="comprehensive"):
    """
    Generate different types of summaries based on the summary_type parameter.
    Types: 'comprehensive', 'executive', 'bullet_points', 'key_topics'
    """
    try:
        combined_doc = " "
        for doc in docs:
            combined_doc += " " + doc.page_content
        
        if summary_type == "executive":
            template = f"""
                        Create an executive summary of the following YouTube video transcript: {combined_doc}
                        
                        Provide a concise, professional summary suitable for executives or busy professionals. Include:
                        
                        * **Executive Overview:** 2-3 sentence summary of the main topic
                        * **Key Insights:** 3-5 most important points or findings
                        * **Business Implications:** Any relevant business or practical applications
                        * **Action Items:** What viewers should do with this information
                        
                        Keep it under 300 words and focus on actionable insights.
                        """
        elif summary_type == "bullet_points":
            template = f"""
                        Create a bullet-point summary of the following YouTube video transcript: {combined_doc}
                        
                        Format as clear, concise bullet points organized by:
                        
                        **Main Topic:**
                        • [Brief description]
                        
                        **Key Points:**
                        • [Point 1]
                        • [Point 2]
                        • [Point 3]
                        • [etc.]
                        
                        **Important Details:**
                        • [Detail 1]
                        • [Detail 2]
                        • [etc.]
                        
                        **Conclusion:**
                        • [Main takeaway]
                        
                        Use clear, concise language and focus on the most important information.
                        """
        elif summary_type == "key_topics":
            template = f"""
                        Analyze the following YouTube video transcript and extract key topics: {combined_doc}
                        
                        Identify and organize the content by main topics:
                        
                        **Topic 1: [Topic Name]**
                        - Key points discussed
                        - Important details
                        
                        **Topic 2: [Topic Name]**
                        - Key points discussed
                        - Important details
                        
                        **Topic 3: [Topic Name]**
                        - Key points discussed
                        - Important details
                        
                        **Cross-cutting Themes:**
                        - Themes that appear across multiple topics
                        
                        Focus on organizing information thematically for easy reference.
                        """
        else:  # comprehensive (default)
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
                        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        results = response.text
        
        # Don't remove newlines for better formatting in bullet points and topics
        if summary_type in ["bullet_points", "key_topics"]:
            return results
        else:
            results = results.replace("\n", " ")
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
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
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
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        results = response.text
        return results
    except Exception as e:
        raise ValueError(f"Failed to optimize the question: {str(e)}")

def generate_suggested_questions(docs, num_questions=5):
    """Generate relevant questions based on the video content."""
    try:
        combined_doc = " ".join([doc.page_content for doc in docs[:3]])  # Use first 3 chunks
        
        template = f"""
                    Based on the following YouTube video transcript, generate {num_questions} thoughtful and relevant questions that viewers might want to ask about the content: {combined_doc}
                    
                    Generate questions that:
                    1. Cover different aspects of the content
                    2. Range from basic understanding to deeper analysis
                    3. Are specific to the video content
                    4. Would help viewers learn more about the topic
                    
                    Format your response as a numbered list:
                    1. [Question 1]
                    2. [Question 2]
                    3. [Question 3]
                    4. [Question 4]
                    5. [Question 5]
                    
                    Make each question clear, specific, and engaging.
                    """
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        
        # Parse questions into a list
        questions_text = response.text
        questions = []
        for line in questions_text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("•") or line.startswith("-")):
                # Remove numbering and clean up
                question = re.sub(r"^\d+\.?\s*", "", line)
                question = re.sub(r"^[•\-]\s*", "", question)
                if question:
                    questions.append(question.strip())
        
        return questions[:num_questions]  # Ensure we do not exceed requested number
        
    except Exception as e:
        raise ValueError(f"Failed to generate suggested questions: {str(e)}")

def extract_key_topics(docs, num_topics=5):
    """Extract key topics from the video content."""
    try:
        combined_doc = " ".join([doc.page_content for doc in docs])
        
        template = f"""
                    Analyze the following YouTube video transcript and extract the {num_topics} most important topics or themes: {combined_doc}
                    
                    For each topic, provide:
                    - A clear, concise topic name (2-4 words)
                    - A brief description (1-2 sentences)
                    
                    Format your response as:
                    **Topic 1: [Topic Name]**
                    [Brief description]
                    
                    **Topic 2: [Topic Name]**
                    [Brief description]
                    
                    Focus on the main themes, concepts, or subjects discussed in the video.
                    """
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        
        return response.text
        
    except Exception as e:
        raise ValueError(f"Failed to extract key topics: {str(e)}")

def get_enhanced_search_results(db, query, k=12):
    """Get search results with relevance scores and better formatting."""
    try:
        results = db.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score),
                "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        # Sort by relevance (lower score = more relevant in FAISS)
        formatted_results.sort(key=lambda x: x["relevance_score"])
        
        return formatted_results
        
    except Exception as e:
        raise ValueError(f"Failed to get enhanced search results: {str(e)}")

def analyze_video_sentiment(docs):
    """Analyze the overall sentiment and tone of the video."""
    try:
        combined_doc = " ".join([doc.page_content for doc in docs[:5]])  # Use first 5 chunks
        
        template = f"""
                    Analyze the sentiment and tone of the following YouTube video transcript: {combined_doc}
                    
                    Provide analysis on:
                    
                    **Overall Sentiment:**
                    - Positive, Negative, or Neutral
                    - Confidence level (High/Medium/Low)
                    
                    **Emotional Tone:**
                    - Describe the general emotional tone (e.g., enthusiastic, serious, conversational, educational, etc.)
                    
                    **Speaker Attitude:**
                    - How does the speaker appear to feel about the topic?
                    
                    **Content Mood:**
                    - Is the content uplifting, concerning, informative, entertaining, etc.?
                    
                    **Key Emotional Indicators:**
                    - Specific words or phrases that indicate the sentiment
                    
                    Keep the analysis objective and based solely on the transcript content.
                    """
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(template)
        if not response.text:
            raise ValueError("No response text found.")
        
        return response.text
        
    except Exception as e:
        raise ValueError(f"Failed to analyze video sentiment: {str(e)}")

# Comparative Analysis Functions
def compare_videos_analysis(videos_data, aspects, depth):
    """Compare multiple videos based on specified aspects"""
    try:
        # Prepare comparison data
        comparison_template = f"""
        You are an expert content analyst. Compare the following {len(videos_data)} YouTube videos based on these aspects: {', '.join(aspects)}.
        
        Analysis Depth: {depth}
        
        Videos to Compare:
        """
        
        for i, video in enumerate(videos_data, 1):
            metadata = video.get('metadata', {})
            analysis = video.get('analysis', {})
            
            comparison_template += f"""
            
            **Video {i}: {metadata.get('title', 'Unknown Title')}**
            - Channel: {metadata.get('author_name', 'Unknown')}
            - URL: {video.get('url', '')}
            - Summary: {analysis.get('summary', 'No summary available')[:300]}...
            - Topics: {analysis.get('topics', 'No topics available')[:200]}...
            - Sentiment: {analysis.get('sentiment', 'No sentiment analysis')[:150]}...
            """
        
        comparison_template += f"""
        
        **Comparison Analysis Instructions:**
        
        1. **Content Comparison**: Compare the main topics, themes, and key points discussed in each video.
        
        2. **Approach Analysis**: How do the creators approach their subjects differently?
        
        3. **Sentiment Comparison**: Compare the emotional tone and sentiment across videos.
        
        4. **Depth & Quality**: Evaluate the depth of coverage and quality of information.
        
        5. **Target Audience**: Identify the intended audience for each video.
        
        6. **Unique Insights**: What unique perspectives or insights does each video offer?
        
        7. **Complementary Content**: How do these videos complement each other?
        
        8. **Recommendations**: Which video would you recommend for different types of viewers and why?
        
        **Format your response with clear sections:**
        - **Overview Summary**
        - **Content Comparison**
        - **Approach & Style Analysis**
        - **Sentiment Analysis**
        - **Quality Assessment**
        - **Audience Targeting**
        - **Unique Value Propositions**
        - **Complementary Insights**
        - **Recommendations**
        """
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(comparison_template)
        
        if not response.text:
            raise ValueError("No comparison response generated.")
        
        # Parse and structure the comparison results
        comparison_results = {
            "comparison_analysis": response.text,
            "videos_count": len(videos_data),
            "aspects_analyzed": aspects,
            "analysis_depth": depth,
            "summary_stats": {
                "total_videos": len(videos_data),
                "channels": len(set(v.get('metadata', {}).get('author_name', 'Unknown') for v in videos_data)),
                "topics_covered": len(set(topic for v in videos_data for topic in str(v.get('analysis', {}).get('topics', '')).split() if topic))
            }
        }
        
        return comparison_results
        
    except Exception as e:
        raise ValueError(f"Failed to compare videos: {str(e)}")

def analyze_video_trends(videos_data, time_period, aspects, grouping):
    """Analyze trends across multiple videos over time"""
    try:
        # Prepare trend analysis data
        trend_template = f"""
        You are an expert trend analyst. Analyze trends across these {len(videos_data)} YouTube videos based on:
        - Time Period: {time_period}
        - Aspects: {', '.join(aspects)}
        - Grouping Method: {grouping}
        
        Videos for Trend Analysis:
        """
        
        # Group videos by specified criteria
        grouped_videos = group_videos_for_analysis(videos_data, grouping)
        
        for group_name, group_videos in grouped_videos.items():
            trend_template += f"""
            
            **{group_name}** ({len(group_videos)} videos):
            """
            
            for video in group_videos:
                metadata = video.get('metadata', {})
                analysis = video.get('analysis', {})
                
                trend_template += f"""
                - {metadata.get('title', 'Unknown')[:100]}...
                  Topics: {str(analysis.get('topics', ''))[:150]}...
                  Sentiment: {str(analysis.get('sentiment', ''))[:100]}...
                """
        
        trend_template += f"""
        
        **Trend Analysis Instructions:**
        
        1. **Topic Evolution**: How have the main topics evolved over the analyzed period/grouping?
        
        2. **Sentiment Trends**: What sentiment patterns emerge across the videos?
        
        3. **Content Depth Trends**: How has the depth and complexity of content changed?
        
        4. **Engagement Patterns**: What patterns can you identify in how content is presented?
        
        5. **Emerging Themes**: What new themes or topics are emerging?
        
        6. **Declining Themes**: What topics are becoming less prominent?
        
        7. **Consistency Patterns**: What remains consistent across the videos?
        
        8. **Innovation Trends**: How are creators innovating in their approach?
        
        9. **Audience Adaptation**: How is content adapting to audience preferences?
        
        10. **Future Predictions**: Based on these trends, what might we expect to see next?
        
        **Format your response with clear sections:**
        - **Trend Overview**
        - **Topic Evolution Analysis**
        - **Sentiment Trend Patterns**
        - **Content Quality Trends**
        - **Engagement & Presentation Trends**
        - **Emerging vs Declining Themes**
        - **Consistency & Innovation Balance**
        - **Audience & Market Adaptation**
        - **Future Trend Predictions**
        - **Key Insights & Recommendations**
        """
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(trend_template)
        
        if not response.text:
            raise ValueError("No trend analysis response generated.")
        
        # Structure the trend results
        trends = {
            "trend_analysis": response.text,
            "analysis_period": time_period,
            "aspects_analyzed": aspects,
            "grouping_method": grouping,
            "data_summary": {
                "total_videos": len(videos_data),
                "groups_analyzed": len(grouped_videos),
                "channels_involved": len(set(v.get('metadata', {}).get('author_name', 'Unknown') for v in videos_data)),
                "analysis_date": datetime.now().isoformat()
            },
            "grouped_data": grouped_videos
        }
        
        return trends
        
    except Exception as e:
        raise ValueError(f"Failed to analyze video trends: {str(e)}")

def group_videos_for_analysis(videos_data, grouping_method):
    """Group videos based on the specified method"""
    try:
        grouped = {}
        
        if grouping_method == "temporal":
            # Group by time periods (simplified - by month for now)
            for video in videos_data:
                # For now, group all videos together since we don't have upload dates
                # In a real implementation, you'd parse upload dates from metadata
                group_key = "All Videos (Temporal grouping requires upload dates)"
                if group_key not in grouped:
                    grouped[group_key] = []
                grouped[group_key].append(video)
                
        elif grouping_method == "topical":
            # Group by similar topics
            for video in videos_data:
                topics = str(video.get('analysis', {}).get('topics', ''))
                # Simple topic grouping - you could implement more sophisticated clustering
                if 'technology' in topics.lower() or 'tech' in topics.lower():
                    group_key = "Technology"
                elif 'education' in topics.lower() or 'learning' in topics.lower():
                    group_key = "Education"
                elif 'business' in topics.lower() or 'marketing' in topics.lower():
                    group_key = "Business"
                else:
                    group_key = "General Content"
                    
                if group_key not in grouped:
                    grouped[group_key] = []
                grouped[group_key].append(video)
                
        elif grouping_method == "channel":
            # Group by channel/creator
            for video in videos_data:
                channel = video.get('metadata', {}).get('author_name', 'Unknown Channel')
                if channel not in grouped:
                    grouped[channel] = []
                grouped[channel].append(video)
                
        else:
            # Default: group all together
            grouped["All Videos"] = videos_data
            
        return grouped
        
    except Exception as e:
        return {"All Videos": videos_data}

def generate_trend_insights(trends_data, videos_data):
    """Generate actionable insights from trend analysis"""
    try:
        insights_template = f"""
        Based on the trend analysis of {len(videos_data)} videos, generate 5-10 key actionable insights that would be valuable for:
        - Content creators
        - Marketers
        - Researchers
        - Business strategists
        
        Trend Analysis Data:
        {str(trends_data.get('trend_analysis', ''))[:1000]}...
        
        Generate insights that are:
        1. Specific and actionable
        2. Based on observable patterns
        3. Useful for decision-making
        4. Forward-looking when possible
        
        Format as a numbered list with brief explanations.
        """
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(insights_template)
        
        if not response.text:
            return ["Unable to generate insights at this time."]
        
        # Parse insights into a list
        insights_text = response.text
        insights = []
        for line in insights_text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("•") or line.startswith("-")):
                # Remove numbering and clean up
                insight = re.sub(r"^\d+\.?\s*", "", line)
                insight = re.sub(r"^[•\-]\s*", "", insight)
                if insight:
                    insights.append(insight.strip())
        
        return insights[:10]  # Limit to 10 insights
        
    except Exception as e:
        return [f"Error generating insights: {str(e)}"]
