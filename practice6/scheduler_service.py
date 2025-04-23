import httpx
import asyncio
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Scheduler Service")

APP_TOKEN = os.getenv("APP_TOKEN", "YourSuperSecretToken")
CLIENT_SERVICE_URL = os.getenv("CLIENT_SERVICE_URL", "http://client-service:8000")

@app.get("/")
async def root():
    return {"service": "Scheduler Service", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

async def call_client_service():
    """Function to periodically call the client service"""
    while True:
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {APP_TOKEN}"}
                payload = {"content": "Scheduled task running", "user_id": "scheduler"}
                
                print(f"Attempting to call {CLIENT_SERVICE_URL}/process")
                
                response = await client.post(
                    f"{CLIENT_SERVICE_URL}/process",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                print(f"Called client service. Status code: {response.status_code}")
                if response.status_code == 200:
                    print(f"Response: {response.json()}")
                else:
                    print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error calling client service: {str(e)}")

        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(call_client_service())
