FROM python:3.12-alpine

WORKDIR /app

COPY practice6/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY practice5/client_service.py .
COPY practice5/.env .

EXPOSE 8000

CMD ["uvicorn", "client_service:app", "--host", "0.0.0.0", "--port", "8000"]
