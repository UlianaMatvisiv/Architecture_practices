import requests
import json
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_SERVICE_URL = os.getenv("CLIENT_SERVICE_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("APP_TOKEN", "REPLACE_WITH_A_LONG_RANDOM_SECRET")
if AUTH_TOKEN == "REPLACE_WITH_A_LONG_RANDOM_SECRET":
    print("WARNING: Using a default token. Please set a secure APP_TOKEN in your .env file.")

def make_request(endpoint, method="GET", payload=None):
    """Make a request to the client service with authentication"""
    url = f"{CLIENT_SERVICE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Making {method} request to {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None

def check_health():
    """Check the health of all services via the client service"""
    print("\n=== Checking Health of Services ===")
    response = requests.get(f"{CLIENT_SERVICE_URL}/health")
    
    if response.status_code == 200:
        health_info = response.json()
        print(f"Client Service: {health_info['status']}")
        
        for service, status in health_info.get('dependencies', {}).items():
            print(f"{service.replace('_', ' ').title()}: {status}")
        
        all_healthy = (health_info['status'] == 'ok' and 
                       all(status == 'ok' for status in health_info.get('dependencies', {}).values()))
        
        if all_healthy:
            print("✅ All services are healthy!")
        else:
            print("❌ Some services are not healthy. Please check the services.")
            sys.exit(1)
    else:
        print(f"❌ Failed to check health: {response.status_code} - {response.text}")
        sys.exit(1)

def test_process_endpoint():
    """Test the /process endpoint with sample data"""
    print("\n=== Testing Process Endpoint ===")
    user_id = "test_user_1"
    payload = {
        "content": "This is a great sample text that we want to process for testing. I like this microservice architecture!",
        "user_id": user_id
    }
    
    print(f"Sending request for user {user_id} with content: '{payload['content']}'")
    response = make_request("/process", method="POST", payload=payload)
    
    if response and response.status_code == 200:
        result = response.json()
        print("\nProcess Result:")
        print(f"- Message: {result.get('message')}")
        print(f"- User ID: {result.get('user_id')}")
        
        processed = result.get('processed_result', {}).get('analysis', {})
        if processed:
            print("\nAnalysis:")
            print(f"- Word Count: {processed.get('word_count')}")
            print(f"- Character Count: {processed.get('character_count')}")
            print(f"- Sentiment: {processed.get('sentiment')}")
            print(f"- Processing ID: {processed.get('processing_id')}")
        
        print("\n✅ First request successful!")
    else:
        status = response.status_code if response else "Failed to connect"
        print(f"❌ Error: {status}")
        if response:
            print(response.text)
        return
    
    # Second request for the same user to demonstrate history
    time.sleep(1)
    print("\n=== Making a second request for the same user ===")
    payload = {
        "content": "This is second sample text for test. The weather is great today.",
        "user_id": user_id
    }
    
    print(f"Sending request for user {user_id} with content: '{payload['content']}'")
    response = make_request("/process", method="POST", payload=payload)
    
    if response and response.status_code == 200:
        result = response.json()
        
        processed = result.get('processed_result', {}).get('analysis', {})
        if processed:
            print("\nNew Analysis:")
            print(f"- Word Count: {processed.get('word_count')}")
            print(f"- Character Count: {processed.get('character_count')}")
            print(f"- Sentiment: {processed.get('sentiment')}")
        
        history = result.get('processed_result', {}).get('process_history', [])
        if len(history) > 1:
            print("\nProcess History:")
            for i, entry in enumerate(history):
                print(f"  {i+1}. Timestamp: {entry.get('timestamp')}")
                print(f"     Word Count: {entry.get('word_count')}")
                print(f"     Sentiment: {entry.get('sentiment')}")
        
        print("\n✅ Second request successful!")
    else:
        status = response.status_code if response else "Failed to connect"
        print(f"❌ Error: {status}")
        if response:
            print(response.text)

def test_invalid_token():
    """Test with an invalid token to verify auth mechanism"""
    print("\n=== Testing Invalid Authentication ===")
    
    url = f"{CLIENT_SERVICE_URL}/process"
    headers = {
        "Authorization": "Bearer InvalidToken",
        "Content-Type": "application/json"
    }
    payload = {
        "content": "This should not be processed",
        "user_id": "unauthorized_user"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 401:
            print("✅ Authentication works correctly! Unauthorized request was properly rejected.")
        else:
            print(f"❌ Expected 401 Unauthorized, but got {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
def test_direct_access_to_business_service():
    """Test direct access to the Business Logic Service's /process endpoint."""
    print("\n=== Testing Direct Access to Business Logic Service ===")
    business_service_url = "http://localhost:8001/process"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": "This is a direct request to the Business Logic Service!",
        "user_id": "test_user_1"
    }
    
    try:
        response = requests.post(business_service_url, headers=headers, json=payload)
        
        if response.status_code == 401:
            print("✅ Direct access blocked as expected! Unauthorized request to Business Logic Service was rejected.")
        else:
            print(f"❌ Expected 401 Unauthorized, but got {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

def main():
    print("=== Microservices Test Script ===")
    print(f"Target Client Service: {CLIENT_SERVICE_URL}")
    print("Waiting for services to be ready...")
    time.sleep(2)
    check_health()
    test_process_endpoint()
    test_invalid_token()
    test_direct_access_to_business_service()

    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()
