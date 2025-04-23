import requests
import json

def test_client_service():
    url = "http://localhost:8000/process"
    headers = {
        "Authorization": "Bearer YourSuperSecretToken",
        "Content-Type": "application/json"
    }
    payload = {
        "content": "Testing the containerized setup",
        "user_id": "test_user"
    }
    
    try:
        print("Sending request to client service...")
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Request successful!")
            print(f"Status code: {response.status_code}")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response:")
            print(response.text)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    test_client_service()
