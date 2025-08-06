"""Test script for file upload functionality."""

import asyncio
import requests
import json
from pathlib import Path

# Create a test file
test_file_path = Path("/tmp/test_upload.txt")
test_file_path.write_text("This is a test file for upload functionality testing.")

def test_file_upload():
    """Test file upload endpoint"""
    
    # First get authentication (you'll need to have a session)
    # For now, let's test the health endpoint to see if the API is running
    
    try:
        # Test health endpoint
        health_response = requests.get("http://localhost:8000/api/v1/health")
        print(f"Health check status: {health_response.status_code}")
        print(f"Health check response: {health_response.json()}")
        
        # Test file upload endpoint (this will fail without auth, but we can see the error)
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_upload.txt', f, 'text/plain')}
            data = {'category': 'documents', 'is_public': 'false'}
            
            upload_response = requests.post(
                "http://localhost:8000/api/v1/files/upload",
                files=files,
                data=data
            )
            
        print(f"Upload status: {upload_response.status_code}")
        print(f"Upload response: {upload_response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()

if __name__ == "__main__":
    test_file_upload()