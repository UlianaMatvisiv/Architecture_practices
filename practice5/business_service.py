from fastapi import Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel
import time
import random
import os

app = FastAPI(title="Business Logic Service",
              description="Handles data processing and transformation")

INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "YourInternalToken")
class ProcessPayload(BaseModel):
    content: str
    existing_data: dict = {}

def validate_internal_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split("Bearer ")[1]
    if token != INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized access to Business Logic Service")
    
    return token

@app.get("/")
async def root():
    return {
        "service": "Business Logic Service",
        "description": "Performs data processing and transformations",
        "endpoints": ["/process", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/process")
async def process_data(payload: ProcessPayload, token: str = Depends(validate_internal_token)):
    time.sleep(2)
    
    # Generate a simple transformation of the input data
    word_count = len(payload.content.split())
    char_count = len(payload.content)
    
    # Access history from existing data if available
    previous_processes = payload.existing_data.get("process_history", [])
    
    # Analyze sentiment
    positive_words = ["good", "great", "excellent", "happy", "positive", "nice", "love", "like"]
    negative_words = ["bad", "terrible", "awful", "sad", "negative", "hate", "dislike"]
    
    words = payload.content.lower().split()
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    result = {
        "analysis": {
            "word_count": word_count,
            "character_count": char_count,
            "sentiment": sentiment,
            "processing_id": f"proc_{random.randint(1000, 9999)}"
        },
        "process_history": previous_processes + [{
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": word_count,
            "sentiment": sentiment
        }]
    }
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("business_service:app", host="0.0.0.0", port=8001, reload=True)
