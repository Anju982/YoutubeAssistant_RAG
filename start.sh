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

# Function to start backend
start_backend() {
    echo -e "${GREEN}🚀 Starting FastAPI backend...${NC}"
    source venv/bin/activate
    
    # Check if running in network mode
    if [ "$NETWORK_MODE" = "true" ]; then
        LOCAL_IP=$(hostname -I | awk '{print $1}')
        echo -e "🌐 Network mode enabled - Backend accessible at: ${BLUE}http://$LOCAL_IP:8001${NC}"
        python -m uvicorn api:app --host 0.0.0.0 --port 8001 --reload &
    else
        python -m uvicorn api:app --host 127.0.0.1 --port 8001 --reload &
    fi
    
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    if [ "$NETWORK_MODE" != "true" ]; then
        echo -e "🔗 Backend API: ${BLUE}http://localhost:8001${NC}"
    fi
}

# Function to start frontend
start_frontend() {
    echo -e "${GREEN}🎨 Starting Streamlit frontend...${NC}"
    source venv/bin/activate
    
    # Set environment variables for network mode
    if [ "$NETWORK_MODE" = "true" ]; then
        LOCAL_IP=$(hostname -I | awk '{print $1}')
        export FASTAPI_HOST="$LOCAL_IP"
        export FASTAPI_PORT="8001"
        echo -e "🌐 Network mode enabled - Frontend accessible at: ${BLUE}http://$LOCAL_IP:8501${NC}"
        streamlit run frontend_api.py --server.address 0.0.0.0 --server.port 8501 &
    else
        streamlit run frontend_api.py --server.port 8501 &
    fi
    
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    if [ "$NETWORK_MODE" != "true" ]; then
        echo -e "🌐 Frontend Interface: ${BLUE}http://localhost:8501${NC}"
    fi
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
    "network")
        echo -e "${BLUE}🌐 Starting in network mode...${NC}"
        LOCAL_IP=$(hostname -I | awk '{print $1}')
        echo -e "📋 Access URLs:"
        echo -e "   Frontend: ${BLUE}http://$LOCAL_IP:8501${NC}"
        echo -e "   Backend:  ${BLUE}http://$LOCAL_IP:8001${NC}"
        echo ""
        export NETWORK_MODE=true
        start_backend
        sleep 3
        start_frontend
        echo -e "${GREEN}🎉 Both services started in network mode!${NC}"
        echo -e "${YELLOW}💡 Other devices can now access the application${NC}"
        echo -e "Press Ctrl+C to stop all services"
        wait
        ;;
    "backend-network")
        echo -e "${BLUE}🌐 Starting backend in network mode...${NC}"
        LOCAL_IP=$(hostname -I | awk '{print $1}')
        echo -e "Backend accessible at: ${BLUE}http://$LOCAL_IP:8001${NC}"
        export NETWORK_MODE=true
        start_backend
        echo -e "${GREEN}Press Ctrl+C to stop the backend${NC}"
        wait $BACKEND_PID
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
        echo "Usage: $0 [backend|frontend|both|network|backend-network|test|test-new]"
        echo "  backend          - Start only FastAPI backend (localhost)"
        echo "  frontend         - Start only Streamlit frontend (localhost)"  
        echo "  both             - Start both services (localhost, default)"
        echo "  network          - Start both services for network access"
        echo "  backend-network  - Start only backend for network access"
        echo "  test             - Run API tests"
        echo "  test-new         - Test new Comparative & Trend Analysis features"
        echo ""
        echo "Network mode allows access from other devices on the same network"
        exit 1
        ;;
esac
