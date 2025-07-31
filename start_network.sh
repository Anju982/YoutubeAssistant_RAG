#!/bin/bash

# YouTube Assistant - Network Setup Script
# This script helps you start the application for network access

echo "🎥 YouTube Assistant - Network Setup"
echo "======================================"

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ Could not detect local IP address"
    echo "Please run the backend manually with:"
    echo "uvicorn api:app --host 0.0.0.0 --port 8001"
    exit 1
fi

echo "🔍 Detected local IP: $LOCAL_IP"
echo ""

# Function to start backend
start_backend() {
    echo "🚀 Starting FastAPI backend for network access..."
    echo "Backend will be accessible at: http://$LOCAL_IP:8001"
    echo ""
    
    # Set environment variables for network mode
    export FASTAPI_HOST="$LOCAL_IP"
    export FASTAPI_PORT="8001"
    
    # Start FastAPI backend
    if command -v uvicorn &> /dev/null; then
        uvicorn api:app --host 0.0.0.0 --port 8001 --reload
    else
        echo "❌ uvicorn not found. Please install it with:"
        echo "pip install uvicorn"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Streamlit frontend..."
    echo "Frontend will be accessible at: http://$LOCAL_IP:8501"
    echo ""
    
    # Set environment variables
    export FASTAPI_HOST="$LOCAL_IP"
    export FASTAPI_PORT="8001"
    
    # Start Streamlit frontend
    if command -v streamlit &> /dev/null; then
        streamlit run frontend_api.py --server.address 0.0.0.0 --server.port 8501
    else
        echo "❌ streamlit not found. Please install it with:"
        echo "pip install streamlit"
        exit 1
    fi
}

# Function to start both
start_both() {
    echo "🚀 Starting both backend and frontend..."
    echo ""
    echo "Backend: http://$LOCAL_IP:8001"
    echo "Frontend: http://$LOCAL_IP:8501"
    echo ""
    echo "Press Ctrl+C to stop both services"
    echo ""
    
    # Set environment variables
    export FASTAPI_HOST="$LOCAL_IP"
    export FASTAPI_PORT="8001"
    
    # Start backend in background
    echo "Starting backend..."
    uvicorn api:app --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    
    sleep 3
    
    # Start frontend
    echo "Starting frontend..."
    streamlit run frontend_api.py --server.address 0.0.0.0 --server.port 8501 &
    FRONTEND_PID=$!
    
    # Function to cleanup on exit
    cleanup() {
        echo ""
        echo "🛑 Stopping services..."
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Services stopped"
        exit 0
    }
    
    # Set trap for cleanup
    trap cleanup INT TERM
    
    # Wait for processes
    wait
}

# Show menu
echo "Choose an option:"
echo "1) Start backend only (for network access)"
echo "2) Start frontend only"
echo "3) Start both backend and frontend"
echo "4) Show network access instructions"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        start_backend
        ;;
    2)
        start_frontend
        ;;
    3)
        start_both
        ;;
    4)
        echo ""
        echo "📋 Network Access Instructions:"
        echo "==============================="
        echo ""
        echo "1. **Start the backend for network access:**"
        echo "   uvicorn api:app --host 0.0.0.0 --port 8001"
        echo ""
        echo "2. **Start the frontend for network access:**"
        echo "   streamlit run frontend_api.py --server.address 0.0.0.0 --server.port 8501"
        echo ""
        echo "3. **Access from other devices:**"
        echo "   - Frontend: http://$LOCAL_IP:8501"
        echo "   - Backend API: http://$LOCAL_IP:8001"
        echo ""
        echo "4. **Configure firewall (if needed):**"
        echo "   - Allow incoming connections on ports 8501 and 8001"
        echo "   - Ubuntu/Debian: sudo ufw allow 8501 && sudo ufw allow 8001"
        echo ""
        echo "5. **Update API URL in the app:**"
        echo "   - Open the frontend web interface"
        echo "   - Go to sidebar > API Configuration"
        echo "   - Enter: http://$LOCAL_IP:8001"
        echo "   - Click 'Update API URL'"
        echo ""
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac
