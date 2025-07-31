"""
FastAPI Backend for YouTube Assistant
Provides REST API endpoints for video analysis and chat functionality
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
import logging
import os

# Import our existing helper functions
import UIHelper as helper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🎥 YouTube Assistant API",
    description="""
    **Advanced AI-powered YouTube video analysis and chat API**
    
    Developed by **Anjana Urulugastenna** - Quantitative Analyst & AI Engineer
    
    🌐 **Website:** [anjanau.com](https://anjanau.com/)
    
    ## Features
    - **Single Video Analysis:** AI-powered summarization, sentiment analysis, and topic extraction
    - **Comparative Analysis:** Compare 2-10 videos to identify similarities and differences  
    - **Trend Analysis:** Analyze patterns across 3-50 videos over time
    - **Interactive Chat:** RAG-powered Q&A with video content
    - **Background Processing:** Async analysis with real-time status monitoring
    
    ## Technologies
    - **AI Model:** Google Gemini 1.5 Flash
    - **Vector Database:** FAISS with Sentence Transformers
    - **Framework:** FastAPI with Pydantic validation
    - **Architecture:** RAG (Retrieval-Augmented Generation)
    
    ---
    © 2025 Anjana Urulugastenna. All rights reserved.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Anjana Urulugastenna",
        "url": "https://anjanau.com/",
    },
    license_info={
        "name": "All Rights Reserved",
        "url": "https://anjanau.com/",
    },
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use Redis in production)
video_cache = {}
analysis_cache = {}
chat_sessions = {}
comparison_cache = {}
trend_analysis_cache = {}

# Pydantic Models
class VideoRequest(BaseModel):
    url: HttpUrl
    summary_type: str = "comprehensive"
    include_sentiment: bool = False
    include_topics: bool = True
    include_questions: bool = True

class ChatMessage(BaseModel):
    session_id: str
    message: str
    use_external_sources: bool = False

class VideoResponse(BaseModel):
    video_id: str
    metadata: Dict[str, Any]
    status: str
    processing_time: float

class AnalysisResponse(BaseModel):
    video_id: str
    summary: str
    topics: Optional[str] = None
    questions: Optional[List[str]] = None
    sentiment: Optional[str] = None
    processing_time: float

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[str]
    processing_time: float

class CompareVideosRequest(BaseModel):
    video_urls: List[HttpUrl]
    comparison_aspects: List[str] = ["topics", "sentiment", "key_points", "conclusions"]
    analysis_depth: str = "comprehensive"

class CompareVideosResponse(BaseModel):
    comparison_id: str
    videos: List[Dict[str, Any]]
    comparison_results: Dict[str, Any]
    processing_time: float

class TrendAnalysisRequest(BaseModel):
    video_urls: List[HttpUrl]
    time_period: Optional[str] = "all"  # "week", "month", "quarter", "year", "all"
    trend_aspects: List[str] = ["topics", "sentiment", "engagement_patterns"]
    grouping: str = "temporal"  # "temporal", "topical", "channel"

class TrendAnalysisResponse(BaseModel):
    analysis_id: str
    videos_analyzed: int
    trends: Dict[str, Any]
    insights: List[str]
    processing_time: float

# Utility Functions
def generate_video_id(url: str) -> str:
    """Generate unique ID for video URL"""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def get_cache_key(video_id: str, analysis_type: str) -> str:
    """Generate cache key for analysis results"""
    return f"{video_id}_{analysis_type}"

# API Endpoints

@app.get("/")
async def root():
    """API Health Check and Information"""
    return {
        "message": "🎥 YouTube Assistant API",
        "description": "AI-powered YouTube video analysis platform",
        "version": "2.0.0",
        "status": "healthy",
        "developer": {
            "name": "Anjana Urulugastenna",
            "title": "Quantitative Analyst & AI Engineer", 
            "website": "https://anjanau.com/"
        },
        "features": [
            "Single Video Analysis",
            "Comparative Analysis", 
            "Trend Analysis",
            "Interactive Chat with RAG",
            "Background Processing"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "compare": "/api/v1/compare",
            "trends": "/api/v1/trends",
            "chat": "/api/v1/chat"
        },
        "copyright": "© 2025 Anjana Urulugastenna. All rights reserved.",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "cache_size": len(video_cache),
        "active_sessions": len(chat_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/analyze", response_model=VideoResponse)
async def analyze_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Analyze a YouTube video and return processing status
    Background processing for better performance
    """
    start_time = datetime.now()
    
    try:
        # Extract video ID and validate URL
        video_url = str(request.url)
        video_id = helper.extract_video_id(video_url)
        
        # Check if video is already being processed
        if video_id in video_cache:
            return VideoResponse(
                video_id=video_id,
                metadata=video_cache[video_id]["metadata"],
                status="already_processed",
                processing_time=0.0
            )
        
        # Start background processing
        background_tasks.add_task(
            process_video_analysis,
            video_id,
            video_url,
            request.summary_type,
            request.include_sentiment,
            request.include_topics,
            request.include_questions
        )
        
        # Return immediate response
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return VideoResponse(
            video_id=video_id,
            metadata={"url": video_url},
            status="processing",
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error analyzing video: {str(e)}")

async def process_video_analysis(
    video_id: str,
    video_url: str,
    summary_type: str,
    include_sentiment: bool,
    include_topics: bool,
    include_questions: bool
):
    """Background task to process video analysis"""
    try:
        logger.info(f"Starting analysis for video {video_id}")
        
        # Load video and create embeddings
        docs, metadata = helper.loadYouTubeVideo(video_url)
        embeddings = helper.embedingFunction()
        db = helper.create_vector_store(docs, embeddings)
        
        # Store in cache
        video_cache[video_id] = {
            "docs": docs,
            "metadata": metadata,
            "db": db,
            "embeddings": embeddings,
            "processed_at": datetime.now(),
            "status": "completed"
        }
        
        # Generate analysis
        analysis_data = {}
        
        # Summary
        summary = helper.sumarizeWithGemini(docs, summary_type)
        analysis_data["summary"] = summary
        
        # Optional analyses
        if include_topics:
            topics = helper.extract_key_topics(docs)
            analysis_data["topics"] = topics
            
        if include_questions:
            questions = helper.generate_suggested_questions(docs)
            analysis_data["questions"] = questions
            
        if include_sentiment:
            sentiment = helper.analyze_video_sentiment(docs)
            analysis_data["sentiment"] = sentiment
        
        # Cache analysis results
        cache_key = get_cache_key(video_id, summary_type)
        analysis_cache[cache_key] = {
            "data": analysis_data,
            "created_at": datetime.now()
        }
        
        logger.info(f"Completed analysis for video {video_id}")
        
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")
        # Update cache with error status
        if video_id in video_cache:
            video_cache[video_id]["status"] = "error"
            video_cache[video_id]["error"] = str(e)

async def process_video_comparison(comparison_id: str, video_urls: List[str], aspects: List[str], depth: str):
    """Background task for comparing multiple videos"""
    try:
        logger.info(f"Starting video comparison {comparison_id}")
        
        videos_data = []
        
        # Process each video
        for i, url in enumerate(video_urls):
            try:
                video_id = generate_video_id(str(url))
                
                # Check if video is already processed
                if video_id not in video_cache or video_cache[video_id].get("status") != "completed":
                    # Process video if not already done
                    docs, metadata = helper.loadYouTubeVideo(str(url))
                    embeddings = helper.embedingFunction()
                    db = helper.create_vector_store(docs, embeddings)
                    
                    # Store in cache
                    video_cache[video_id] = {
                        "docs": docs,
                        "metadata": metadata,
                        "db": db,
                        "embeddings": embeddings,
                        "processed_at": datetime.now(),
                        "status": "completed"
                    }
                    
                    # Generate basic analysis
                    summary = helper.sumarizeWithGemini(docs, "comprehensive")
                    topics = helper.extract_key_topics(docs)
                    sentiment = helper.analyze_video_sentiment(docs)
                    
                    analysis_cache[f"{video_id}_comprehensive"] = {
                        "data": {
                            "summary": summary,
                            "topics": topics,
                            "sentiment": sentiment
                        },
                        "created_at": datetime.now()
                    }
                
                # Collect video data for comparison
                video_info = {
                    "video_id": video_id,
                    "url": str(url),
                    "metadata": video_cache[video_id]["metadata"],
                    "analysis": analysis_cache.get(f"{video_id}_comprehensive", {}).get("data", {})
                }
                videos_data.append(video_info)
                
                # Update progress
                comparison_cache[comparison_id]["videos"] = videos_data
                
            except Exception as e:
                logger.error(f"Error processing video {url}: {str(e)}")
                continue
        
        # Perform comparison analysis
        comparison_results = helper.compare_videos_analysis(videos_data, aspects, depth)
        
        # Update cache with results
        comparison_cache[comparison_id].update({
            "status": "completed",
            "videos": videos_data,
            "comparison_results": comparison_results,
            "completed_at": datetime.now()
        })
        
        logger.info(f"Completed video comparison {comparison_id}")
        
    except Exception as e:
        logger.error(f"Error in video comparison: {str(e)}")
        comparison_cache[comparison_id]["status"] = "error"
        comparison_cache[comparison_id]["error"] = str(e)

async def process_trend_analysis(analysis_id: str, video_urls: List[str], time_period: str, aspects: List[str], grouping: str):
    """Background task for trend analysis across videos"""
    try:
        logger.info(f"Starting trend analysis {analysis_id}")
        
        videos_data = []
        
        # Process each video
        for i, url in enumerate(video_urls):
            try:
                video_id = generate_video_id(str(url))
                
                # Check if video is already processed
                if video_id not in video_cache or video_cache[video_id].get("status") != "completed":
                    # Process video if not already done
                    docs, metadata = helper.loadYouTubeVideo(str(url))
                    embeddings = helper.embedingFunction()
                    db = helper.create_vector_store(docs, embeddings)
                    
                    # Store in cache
                    video_cache[video_id] = {
                        "docs": docs,
                        "metadata": metadata,
                        "db": db,
                        "embeddings": embeddings,
                        "processed_at": datetime.now(),
                        "status": "completed"
                    }
                    
                    # Generate analysis
                    summary = helper.sumarizeWithGemini(docs, "comprehensive")
                    topics = helper.extract_key_topics(docs)
                    sentiment = helper.analyze_video_sentiment(docs)
                    
                    analysis_cache[f"{video_id}_comprehensive"] = {
                        "data": {
                            "summary": summary,
                            "topics": topics,
                            "sentiment": sentiment
                        },
                        "created_at": datetime.now()
                    }
                
                # Collect video data for trend analysis
                video_info = {
                    "video_id": video_id,
                    "url": str(url),
                    "metadata": video_cache[video_id]["metadata"],
                    "analysis": analysis_cache.get(f"{video_id}_comprehensive", {}).get("data", {})
                }
                videos_data.append(video_info)
                
                # Update progress
                trend_analysis_cache[analysis_id]["videos_analyzed"] = len(videos_data)
                
            except Exception as e:
                logger.error(f"Error processing video {url}: {str(e)}")
                continue
        
        # Perform trend analysis
        trends = helper.analyze_video_trends(videos_data, time_period, aspects, grouping)
        insights = helper.generate_trend_insights(trends, videos_data)
        
        # Update cache with results
        trend_analysis_cache[analysis_id].update({
            "status": "completed",
            "videos_analyzed": len(videos_data),
            "trends": trends,
            "insights": insights,
            "completed_at": datetime.now()
        })
        
        logger.info(f"Completed trend analysis {analysis_id}")
        
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        trend_analysis_cache[analysis_id]["status"] = "error"
        trend_analysis_cache[analysis_id]["error"] = str(e)

@app.get("/api/v1/status/{video_id}")
async def get_analysis_status(video_id: str):
    """Get the processing status of a video analysis"""
    if video_id not in video_cache:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_data = video_cache[video_id]
    return {
        "video_id": video_id,
        "status": video_data.get("status", "unknown"),
        "processed_at": video_data.get("processed_at"),
        "metadata": video_data.get("metadata", {}),
        "error": video_data.get("error")
    }

@app.get("/api/v1/analysis/{video_id}", response_model=AnalysisResponse)
async def get_analysis_results(video_id: str, summary_type: str = "comprehensive"):
    """Get completed analysis results for a video"""
    start_time = datetime.now()
    
    # Check if video exists
    if video_id not in video_cache:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_data = video_cache[video_id]
    if video_data.get("status") != "completed":
        raise HTTPException(status_code=202, detail="Analysis still processing")
    
    # Check analysis cache
    cache_key = get_cache_key(video_id, summary_type)
    if cache_key not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    analysis_data = analysis_cache[cache_key]["data"]
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return AnalysisResponse(
        video_id=video_id,
        summary=analysis_data.get("summary", ""),
        topics=analysis_data.get("topics"),
        questions=analysis_data.get("questions"),
        sentiment=analysis_data.get("sentiment"),
        processing_time=processing_time
    )

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_video(message: ChatMessage):
    """Chat with a video using RAG"""
    start_time = datetime.now()
    
    try:
        # Extract video_id from session_id (assuming format: video_id_timestamp)
        video_id = message.session_id.split('_')[0]
        
        if video_id not in video_cache:
            raise HTTPException(status_code=404, detail="Video not found. Analyze video first.")
        
        video_data = video_cache[video_id]
        if video_data.get("status") != "completed":
            raise HTTPException(status_code=202, detail="Video analysis still processing")
        
        # Get relevant context
        db = video_data["db"]
        search_results = helper.get_enhanced_search_results(db, message.message)
        relevant_content = search_results[0]['content'] if search_results else ""
        
        # Generate response
        if message.use_external_sources:
            response = helper.optimizing_question_with_external_info(relevant_content, message.message)
        else:
            response = helper.optimizing_question(relevant_content, message.message)
        
        # Store chat history
        if message.session_id not in chat_sessions:
            chat_sessions[message.session_id] = []
        
        chat_sessions[message.session_id].append({
            "timestamp": datetime.now(),
            "user_message": message.message,
            "assistant_response": response,
            "sources": [result['snippet'] for result in search_results[:3]]
        })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            session_id=message.session_id,
            response=response,
            sources=[result['snippet'] for result in search_results[:3]],
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/api/v1/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in chat_sessions:
        return {"session_id": session_id, "messages": []}
    
    return {
        "session_id": session_id,
        "messages": chat_sessions[session_id]
    }

@app.get("/api/v1/videos")
async def list_processed_videos():
    """List all processed videos"""
    videos = []
    for video_id, data in video_cache.items():
        videos.append({
            "video_id": video_id,
            "title": data.get("metadata", {}).get("title", "Unknown"),
            "channel": data.get("metadata", {}).get("author_name", "Unknown"),
            "status": data.get("status", "unknown"),
            "processed_at": data.get("processed_at")
        })
    
    return {"videos": videos, "total": len(videos)}

@app.delete("/api/v1/cache/{video_id}")
async def clear_video_cache(video_id: str):
    """Clear cache for specific video"""
    if video_id in video_cache:
        del video_cache[video_id]
    
    # Clear related analysis cache
    keys_to_delete = [key for key in analysis_cache.keys() if key.startswith(video_id)]
    for key in keys_to_delete:
        del analysis_cache[key]
    
    return {"message": f"Cache cleared for video {video_id}"}

@app.delete("/api/v1/cache")
async def clear_all_cache():
    """Clear all cache"""
    video_cache.clear()
    analysis_cache.clear()
    chat_sessions.clear()
    comparison_cache.clear()
    trend_analysis_cache.clear()
    
    return {"message": "All cache cleared"}

@app.post("/api/v1/compare", response_model=CompareVideosResponse)
async def compare_videos(request: CompareVideosRequest, background_tasks: BackgroundTasks):
    """Compare multiple videos on similar topics"""
    start_time = datetime.now()
    
    if len(request.video_urls) < 2:
        raise HTTPException(status_code=400, detail="At least 2 videos required for comparison")
    
    if len(request.video_urls) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 videos allowed for comparison")
    
    # Generate comparison ID
    comparison_id = hashlib.md5(str(request.video_urls).encode()).hexdigest()[:12]
    
    # Initialize comparison cache
    comparison_cache[comparison_id] = {
        "status": "processing",
        "videos": [],
        "comparison_results": {},
        "created_at": datetime.now()
    }
    
    # Start background processing
    background_tasks.add_task(
        process_video_comparison,
        comparison_id,
        request.video_urls,
        request.comparison_aspects,
        request.analysis_depth
    )
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return CompareVideosResponse(
        comparison_id=comparison_id,
        videos=[],
        comparison_results={"status": "processing"},
        processing_time=processing_time
    )

@app.get("/api/v1/compare/{comparison_id}")
async def get_comparison_results(comparison_id: str):
    """Get comparison results"""
    if comparison_id not in comparison_cache:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    comparison_data = comparison_cache[comparison_id]
    return {
        "comparison_id": comparison_id,
        "status": comparison_data.get("status", "unknown"),
        "videos": comparison_data.get("videos", []),
        "comparison_results": comparison_data.get("comparison_results", {}),
        "created_at": comparison_data.get("created_at")
    }

@app.post("/api/v1/trends", response_model=TrendAnalysisResponse)
async def analyze_trends(request: TrendAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze trends across multiple videos over time"""
    start_time = datetime.now()
    
    if len(request.video_urls) < 3:
        raise HTTPException(status_code=400, detail="At least 3 videos required for trend analysis")
    
    if len(request.video_urls) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 videos allowed for trend analysis")
    
    # Generate analysis ID
    analysis_id = hashlib.md5(str(request.video_urls).encode()).hexdigest()[:12]
    
    # Initialize trend analysis cache
    trend_analysis_cache[analysis_id] = {
        "status": "processing",
        "videos_analyzed": 0,
        "trends": {},
        "insights": [],
        "created_at": datetime.now()
    }
    
    # Start background processing
    background_tasks.add_task(
        process_trend_analysis,
        analysis_id,
        request.video_urls,
        request.time_period,
        request.trend_aspects,
        request.grouping
    )
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return TrendAnalysisResponse(
        analysis_id=analysis_id,
        videos_analyzed=0,
        trends={"status": "processing"},
        insights=[],
        processing_time=processing_time
    )

@app.get("/api/v1/trends/{analysis_id}")
async def get_trend_results(analysis_id: str):
    """Get trend analysis results"""
    if analysis_id not in trend_analysis_cache:
        raise HTTPException(status_code=404, detail="Trend analysis not found")
    
    trend_data = trend_analysis_cache[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": trend_data.get("status", "unknown"),
        "videos_analyzed": trend_data.get("videos_analyzed", 0),
        "trends": trend_data.get("trends", {}),
        "insights": trend_data.get("insights", []),
        "created_at": trend_data.get("created_at")
    }

# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("🎥 YouTube Assistant API starting up...")
    logger.info("API Documentation available at: /docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🎥 YouTube Assistant API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
