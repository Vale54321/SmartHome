FROM python:3.11-slim

WORKDIR /app
COPY requirenments.txt .
RUN pip install --no-cache-dir -r requirenments.txt

COPY app.py .
COPY battery_modbus_client.py .

CMD ["python", "app.py"]
