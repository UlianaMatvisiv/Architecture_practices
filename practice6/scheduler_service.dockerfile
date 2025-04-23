FROM python:3.12-alpine

WORKDIR /app

COPY practice6/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY practice6/scheduler_service.py .
COPY practice5/.env .

EXPOSE 8003

CMD ["uvicorn", "scheduler_service:app", "--host", "0.0.0.0", "--port", "8003"]
