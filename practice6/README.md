# Containerization with Podman - Homework #3

This repository demonstrates containerizing a microservice-based application using Podman and Podman Compose. The project builds on the previous microservices architecture from practice 5, and adds containerization capabilities.

## Project Structure
### practice5
- `client_service.py` - Public-facing API gateway that orchestrates calls to other services
- `business_service.py` - Handles data processing and business logic
- `database_service.py` - Manages data storage and retrieval
- `.env` - Environment variables for configuration
### practice6
- `scheduler_service.py` - New service that periodically calls the client service
- `*.dockerfile` - Containerization instructions for each service
- `podman-compose.yml` - Multi-container orchestration configuration
- `requirements.txt` - Python dependencies
- `.env` - Environment variables for configuration

## Task #1: Wrap Single Application in Container

This task demonstrates how to containerize the Client Service as a standalone application.

### Building and Running the Container

1. Build the client service container:
   ```bash
   podman build -t client-service -f practice6/client_service.dockerfile .
   ```

2. Run the container:
   ```bash
   podman run -d --name client-service -p 8000:8000 client-service
   ```

3. Test the service:
Here only two endpoints from previous homework are accessible since we did not containerize business logic and database.
   ```bash
   # Test the root endpoint
   curl http://localhost:8000/
   
   # Test the health endpoint
   curl http://localhost:8000/health
   ```

5. Check container logs:
   ```bash
   podman logs client-service
   ```
   ##### INFO:     Started server process [1]
   ##### INFO:     Waiting for application startup.
   ##### INFO:     Application startup complete.
   ##### INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

6. Clean up:
   ```bash
   podman stop client-service
   podman rm client-service
   ```

## Task #2: Multi-container Setup with Local Network

This task demonstrates how to set up multiple containers that communicate with each other using Podman Compose.
For this task I created new FastAPI `scheduler_service.py`.

### Setup and Running

1. Created new Dockerfile and compose file `podman-compose.yml`. Also added Dockerfiles for business service and database service from preactice5 to be able to check the process endpoint.

2. Start all services with Podman Compose:
   ```bash
   podman-compose -f practice6\podman-compose.yml up -d
   ```

4. Verify all containers are running:
   ```bash
   podman-compose -f practice6\podman-compose.yml ps
   ```
![image](https://github.com/user-attachments/assets/fda0616c-4ada-4913-9fd9-a07b6fc4b7b8)

5. Test the communication between services:
   ```bash
   # Check scheduler service logs to see if it's calling the client service
   podman-compose logs scheduler-service
   
   # Make a direct request to the client service using the provided test script
   python test_client_service.py
   ```

6. Clean up when done:
   ```bash
   podman-compose -f practice6/podman-compose.yml down
   ```

## Service Architecture

- **Client Service (Port 8000)**: Entry point for external requests
- **Business Service (Port 8001)**: Handles data processing
- **Database Service (Port 8002)**: Stores and retrieves data
- **Scheduler Service (Port 8003)**: Periodically calls the Client Service

## Testing

You can test the services using the provided `test_client_service.py` script:

This will send a request to the Client Service process endpoint and display the response.

## Notes

- All services use token-based authentication as in practice5
- The services communicate over a private Docker network
- The scheduler calls the client service every 10 seconds
- Environment variables control service URLs and authentication tokens (You need to create .env file in practice5. You can check practice5/README.md)
