from fastapi import FastAPI, Header, HTTPException, Depends
import httpx
import os
from pydantic import BaseModel

BUSINESS_SERVICE_URL = os.getenv("BUSINESS_SERVICE_URL", "http://localhost:8001")
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:8002")
APP_TOKEN = os.getenv("APP_TOKEN", "YourSuperSecretToken")
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "YourInternalToken")

app = FastAPI(title="Client Service", 
              description="The API gateway for our microservice application")

class DataPayload(BaseModel):
    content: str
    user_id: str

def validate_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split("Bearer ")[1]
    if token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

@app.get("/")
async def root():
    return {
        "service": "Client Service",
        "description": "Entry point for the microservice application. This service orchestrates calls to the Business Logic and Database services.",
        "endpoints": ["/process", "/health"]
    }

@app.get("/health")
async def health():
    client_status = "ok"
    business_status = "unknown"
    db_status = "unknown"
    
    async with httpx.AsyncClient() as client:
        try:
            business_response = await client.get(f"{BUSINESS_SERVICE_URL}/health")
            if business_response.status_code == 200:
                business_status = business_response.json().get("status", "error")
        except Exception:
            business_status = "error"
            
        try:
            db_response = await client.get(f"{DATABASE_SERVICE_URL}/health")
            if db_response.status_code == 200:
                db_status = db_response.json().get("status", "error")
        except Exception:
            db_status = "error"
    
    return {
        "status": client_status,
        "dependencies": {
            "business_service": business_status,
            "database_service": db_status
        }
    }

@app.post("/process")
async def process_data(data: DataPayload, token: str = Depends(validate_token)):
    """
    Process data through the orchestrated flow:
    1. Read data from the Database Service
    2. Process it with the Business Logic Service
    3. Store the result in the Database Service
    4. Return the final response
    """
    async with httpx.AsyncClient() as client:
        try:
            db_response = await client.get(
                f"{DATABASE_SERVICE_URL}/read",
                params={"user_id": data.user_id},
                headers={"Authorization": f"Bearer {INTERNAL_SERVICE_TOKEN}"}
            )
            if db_response.status_code != 200:
                return {"error": f"Database read failed: {db_response.text}"}
            
            existing_data = db_response.json()
        except Exception as e:
            return {"error": f"Failed to connect to database service: {str(e)}"}
        try:
            payload = {
                "content": data.content,
                "existing_data": existing_data.get("data", {})
            }
            headers = {
                "Authorization": f"Bearer {INTERNAL_SERVICE_TOKEN}"
            }
            business_response = await client.post(
                f"{BUSINESS_SERVICE_URL}/process",
                json=payload,
                headers=headers
            )
            if business_response.status_code != 200:
                return {"error": f"Business logic processing failed: {business_response.text}"}
            
            processed_result = business_response.json()
        except Exception as e:
            return {"error": f"Failed to connect to business logic service: {str(e)}"}
        try:
            save_payload = {
                "user_id": data.user_id,
                "data": processed_result
            }
            save_response = await client.post(
                f"{DATABASE_SERVICE_URL}/write",
                json=save_payload,
                headers={"Authorization": f"Bearer {INTERNAL_SERVICE_TOKEN}"}
            )
            if save_response.status_code != 200:
                return {"error": f"Database write failed: {save_response.text}"}
            
            final_result = save_response.json()
        except Exception as e:
            return {"error": f"Failed to store result in database: {str(e)}"}
        return {
            "message": "Data processed successfully",
            "user_id": data.user_id,
            "original_content": data.content,
            "processed_result": processed_result,
            "storage_status": final_result
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("client_service:app", host="0.0.0.0", port=8000, reload=True)
