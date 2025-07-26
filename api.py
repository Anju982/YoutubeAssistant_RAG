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
    description="Advanced AI-powered YouTube video analysis and chat API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    """API Health Check"""
    return {
        "message": "🎥 YouTube Assistant API",
        "version": "2.0.0",
        "status": "healthy",
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
    
    return {"message": "All cache cleared"}

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
