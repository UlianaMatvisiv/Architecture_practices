import os
from fastapi import Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

app = FastAPI(title="Database Service",
              description="Handles data storage and retrieval")

INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "YourInternalToken")
database: Dict[str, Dict[str, Any]] = {}

class WritePayload(BaseModel):
    user_id: str
    data: Dict[str, Any]

class ReadParams(BaseModel):
    user_id: str

def validate_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split("Bearer ")[1]
    if token != INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

@app.get("/")
async def root():
    return {
        "service": "Database Service",
        "description": "Handles data storage and retrieval operations",
        "endpoints": ["/write", "/read", "/health"],
        "records_count": len(database)
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/write")
async def write_data(payload: WritePayload, token: str = Depends(validate_token)):
    """
    Write data to the database for a specific user
    """
    user_id = payload.user_id
    data_with_metadata = payload.data.copy()
    data_with_metadata["metadata"] = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": database.get(user_id, {}).get("metadata", {}).get("version", 0) + 1
    }

    database[user_id] = data_with_metadata
    
    return {
        "status": "success",
        "user_id": user_id,
        "message": "Data stored successfully",
        "metadata": data_with_metadata["metadata"]
    }

@app.get("/read")
async def read_data(user_id: str, token: str = Depends(validate_token)):
    """
    Read data from the database for a specific user
    """
    if user_id not in database:
        return {
            "status": "success",
            "user_id": user_id,
            "data": {},
            "message": "No data found for this user"
        }
    
    return {
        "status": "success",
        "user_id": user_id,
        "data": database[user_id],
        "message": "Data retrieved successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("database_service:app", host="0.0.0.0", port=8002, reload=True)
