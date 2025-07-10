FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirenments.txt .
RUN pip install --no-cache-dir -r requirenments.txt

COPY main.py .
COPY clients/ ./clients/

CMD ["python", "main.py"]
