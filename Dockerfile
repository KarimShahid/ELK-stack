FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir boto3

COPY logger.py .

CMD ["python", "logger.py"]