FROM python:3.12-alpine

WORKDIR /app

COPY practice6/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY practice5/business_service.py .
COPY practice5/.env .

EXPOSE 8001

CMD ["uvicorn", "business_service:app", "--host", "0.0.0.0", "--port", "8001"]
