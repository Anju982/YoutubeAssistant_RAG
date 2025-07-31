#!/bin/bash

# YouTube Assistant RAG - Startup Script
# This script helps you start the FastAPI backend and Streamlit frontend

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎥 YouTube Assistant RAG - Startup Script${NC}"
echo "================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Creating .env template..."
    echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
    echo -e "${YELLOW}Please edit .env file and add your Google API key${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Function to start FastAPI backend
start_backend() {
    echo -e "${GREEN}🚀 Starting FastAPI Backend...${NC}"
    python -m uvicorn api:app --reload --port 8001 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    for i in {1..10}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend started successfully!${NC}"
            echo -e "📖 API Documentation: ${BLUE}http://localhost:8001/docs${NC}"
            break
        fi
        sleep 1
    done
}

# Function to start Streamlit frontend
start_frontend() {
    echo -e "${GREEN}🎨 Starting Streamlit Frontend...${NC}"
    streamlit run frontend_api.py --server.port 8501 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    echo -e "🌐 Frontend Interface: ${BLUE}http://localhost:8501${NC}"
}

# Function to cleanup processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true  
        echo "Frontend stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
case "${1:-both}" in
    "backend")
        start_backend
        echo -e "${GREEN}Press Ctrl+C to stop the backend${NC}"
        wait $BACKEND_PID
        ;;
    "frontend")
        start_frontend
        echo -e "${GREEN}Press Ctrl+C to stop the frontend${NC}"
        wait $FRONTEND_PID
        ;;
    "both"|"")
        start_backend
        sleep 3
        start_frontend
        echo -e "${GREEN}🎉 Both services started!${NC}"
        echo -e "Press Ctrl+C to stop all services"
        wait
        ;;
    "test")
        echo -e "${BLUE}🧪 Running API tests...${NC}"
        python test_api.py
        ;;
    "test-new")
        echo -e "${BLUE}🧪 Testing new Comparative & Trend Analysis features...${NC}"
        python test_new_features.py
        ;;
    *)
        echo "Usage: $0 [backend|frontend|both|test|test-new]"
        echo "  backend   - Start only FastAPI backend"
        echo "  frontend  - Start only Streamlit frontend"  
        echo "  both      - Start both services (default)"
        echo "  test      - Run API tests"
        echo "  test-new  - Test new Comparative & Trend Analysis features"
        exit 1
        ;;
esac
