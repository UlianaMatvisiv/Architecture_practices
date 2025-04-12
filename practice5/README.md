# Microservice-Based Application with Token Authentication
This project implements a REST-based microservices application with token authentication using FastAPI. It consists of three interconnected services:
 1. Client Service - The public-facing API gateway
 2.  Business Logic Service - Handles data processing
3.  Database Service - Manages data storage and retrieval

Security Considerations

-   Only Client Service is publicly accessible
-   Two-level token-based authentication prevents direct access to internal services
-   Environment-based configuration
## Setup and Running the Application

### Prerequisites

-   Python 3.8 or higher
-   FastAPI (`pip install fastapi`)
-   Uvicorn (`pip install uvicorn`)
-   Httpx (`pip install httpx`)

### Configure Environment Variables
Create a `.env` file in the project root:

    APP_TOKEN=your_secure_external_token
    INTERNAL_SERVICE_TOKEN=your_secure_internal_token
    CLIENT_SERVICE_URL=http://localhost:8000
    BUSINESS_SERVICE_URL=http://localhost:8001
    DATABASE_SERVICE_URL=http://localhost:8002

### Running the Services

You can start all services at once using the provided startup script:

`python start_services.py`

This will start all three services on different ports:

-   Client Service: [http://localhost:8000](http://localhost:8000)
-   Business Logic Service: [http://localhost:8001](http://localhost:8001)
-   Database Service: [http://localhost:8002](http://localhost:8002)

In addition you can start each service separately if you prefer. Open three terminal windows and run:

1.  Start the Database Service:
> uvicorn database_service:app --host 0.0.0.0 --port 8002 --reload
    
2.  Start the Business Logic Service:
> uvicorn database_service:app --host 0.0.0.0 --port 8001 --reload
    
4.  Start the Client Service:
> uvicorn database_service:app --host 0.0.0.0 --port 8000 --reload

## Authentication & Security
The Client Service uses a simple token-based authentication mechanism:
* External Access
1.  The token is defined in the environment variable `APP_TOKEN` (defaults to "YourSuperSecretToken" if not set)
2.  Clients must include this token in the `Authorization` header as a Bearer token:
    `Authorization: Bearer YourSuperSecretToken`
3.  Requests without a valid token will receive a 401 Unauthorized response
	
* Internal Service Communication
1. The internal service token is defined in the environment variable `INTERNAL_SERVICE_TOKEN` and is required for communication between internal services.
2. Each internal service request includes the `Internal-Service-Token` header
3. The token is validated before processing any inter-service request and if the token is missing or incorrect, the request is immediately rejected with a 403 Forbidden error. This prevents unauthorized services or external clients from directly accessing internal service endpoints and adds an additional layer of security

## Request Flow

1.  External client sends request to Client Service
2.  Client Service validates external token
3.  Client Service retrieves existing data from Database Service
4.  Client Service sends data to the Business Logic Service for processing
5.  Client Service stores the processed results back in the Database Service
6.  Client Service returns the final result to the user

## Quick overview of API endpoints

**1.  Client Service**
Request:
-   POST  `/process`  - Orchestrates data processing.
    -   Headers:  `{ "Authorization": "Bearer <APP_TOKEN>" }`
        
    -   Body:  `{ "content": "string", "user_id": "string" }`
    
**2.  Business Logic Service**
	Request:
-   POST  `/process`  - Processes text data by counting words and characters, analyzing sentiment (positive, negative, or neutral), and maintaining a history of previous analyses.
    
    -   Headers: `{ "Authorization": "Bearer <INTERNAL_SERVICE_TOKEN>" }`
        
    -   Body:  `{ "content": "string", "existing_data": {}}`
        
**3.  Database Service**
Request:
-   GET  `/read`  - Retrieve stored data.
    
    -   Headers: `{ "Authorization": "Bearer <INTERNAL_SERVICE_TOKEN>" }`
        
    -   Query Params:  `user_id=<string>`
        
-   POST  `/write`  - Store processed data.
    
     -   Headers: `{ "Authorization": "Bearer <INTERNAL_SERVICE_TOKEN>" }`
        
    -   Body:  `{ "user_id": "string", "data": {}}`
        

Also all three services expose the following common endpoints (no headers or body required):

-   GET  `/`  - Returns general service details.
    
-   GET  `/health`  - Provides health status of the service.
## Example Usage

A test script is provided to demonstrate how to interact with the services:

`python test_microservices.py`

**What the Test Script Does**

1.  Health Check: Verifies all services are running correctly
2.  Authenticated Request:
    -   Sends a first request with a sample text
    -   Shows processing results including:
        -   Word count
        -   Character count
        -   Sentiment analysis
3.  Multiple Requests:
    -   Sends a second request for the same user
    -   Demonstrates history tracking
4.  Authentication Test:
    -   Attempts a request with an invalid token
    -   Shows proper security rejection
5. Security Test:
	- Attempts to directly access the Business Logic Service without going through the Client Service.
	- Shows proper security rejection
