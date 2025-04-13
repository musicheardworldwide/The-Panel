"""
Test script for The Panel server.

This script sends a simple test request to the server to verify it's working correctly.
"""

import requests
import json
import argparse
from typing import Dict, Any

def test_chat_endpoint(url: str, prompt: str) -> Dict[str, Any]:
    """
    Test the chat endpoint of The Panel server.
    
    Args:
        url: The base URL of the server
        prompt: The prompt to send to the server
        
    Returns:
        The server's response as a dictionary
    """
    # Construct the full endpoint URL
    endpoint = f"{url}/chat"
    
    # Prepare the request payload
    payload = {
        "prompt": prompt
    }
    
    # Send the request
    print(f"Sending request to {endpoint} with prompt: '{prompt}'")
    response = requests.post(
        endpoint,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Request successful!")
        return response.json()
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return {"error": response.text}

def test_health_endpoint(url: str) -> Dict[str, Any]:
    """
    Test the health check endpoint of The Panel server.
    
    Args:
        url: The base URL of the server
        
    Returns:
        The server's health check response as a dictionary
    """
    # Construct the full endpoint URL
    endpoint = f"{url}/health"
    
    # Send the request
    print(f"Checking server health at {endpoint}")
    response = requests.get(endpoint)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Health check successful!")
        return response.json()
    else:
        print(f"Health check failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return {"error": response.text}

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test The Panel server")
    parser.add_argument(
        "--url", 
        default="http://localhost:5001", 
        help="The base URL of the server (default: http://localhost:5001)"
    )
    parser.add_argument(
        "--prompt", 
        default="Hello, how are you?", 
        help="The prompt to send to the server (default: 'Hello, how are you?')"
    )
    parser.add_argument(
        "--health-only", 
        action="store_true", 
        help="Only test the health check endpoint"
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Test the health check endpoint
    health_result = test_health_endpoint(args.url)
    print(f"Health check result: {json.dumps(health_result, indent=2)}")
    
    # Test the chat endpoint if not health-only
    if not args.health_only:
        chat_result = test_chat_endpoint(args.url, args.prompt)
        print(f"Chat result: {json.dumps(chat_result, indent=2)}")