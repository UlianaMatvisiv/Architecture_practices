import subprocess
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

def start_service(file_name, port):
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{file_name}:app", "--host", "0.0.0.0", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():
    services = [
        ("database_service", 8002),
        ("business_service", 8001),
        ("client_service", 8000)
    ]
    app_token = os.getenv("APP_TOKEN")
    if not app_token or app_token == "REPLACE_WITH_A_LONG_RANDOM_SECRET":
        print("ERROR: Please set a secure APP_TOKEN in your .env file")
        sys.exit(1)
    processes = []
    try:
        print("Starting all microservices...")

        for service_file, port in services:
            print(f"Starting {service_file} on port {port}...")
            process = start_service(service_file, port)
            processes.append((service_file, process))
            time.sleep(1)
        
        print("\nAll services started successfully!")
        print("\nAccess points:")
        print("- Client Service: http://localhost:8000")
        print("- Business Logic Service: http://localhost:8001")
        print("- Database Service: http://localhost:8002")
        print("\nPress Ctrl+C to stop all services")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping all services...")
        for service_name, process in processes:
            print(f"Stopping {service_name}...")
            process.terminate()
        print("All services stopped")

if __name__ == "__main__":
    main()
