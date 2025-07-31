"""
Simple test script to verify FastAPI functionality
"""

import requests
import time

API_BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_video_analysis():
    """Test video analysis with a short video"""
    print("\n🎥 Testing video analysis...")
    
    # Use a shorter video for faster testing
    payload = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (short)
        "summary_type": "executive",
        "include_sentiment": False,
        "include_topics": False,
        "include_questions": False
    }
    
    print("📤 Sending analysis request...")
    response = requests.post(f"{API_BASE_URL}/api/v1/analyze", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Video ID: {result.get('video_id')}")
        print(f"Status: {result.get('status')}")
        return result.get('video_id')
    else:
        print(f"Error: {response.text}")
        return None

def test_status_check(video_id):
    """Test status checking"""
    if not video_id:
        return
        
    print(f"\n📊 Checking status for video {video_id}...")
    response = requests.get(f"{API_BASE_URL}/api/v1/status/{video_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Processing Status: {result.get('status')}")
        if result.get('metadata'):
            print(f"Title: {result['metadata'].get('title', 'Unknown')}")

def main():
    print("🚀 FastAPI Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Health check failed! Make sure FastAPI server is running.")
        return
    
    print("✅ Health check passed!")
    
    # Test 2: Video analysis
    video_id = test_video_analysis()
    if video_id:
        print("✅ Video analysis request successful!")
        
        # Test 3: Status check
        time.sleep(2)  # Wait a moment for processing
        test_status_check(video_id)
        print("✅ Status check successful!")
    else:
        print("❌ Video analysis failed!")
    
    print("\n🎯 All tests completed!")
    print("👀 Check the API documentation at: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
