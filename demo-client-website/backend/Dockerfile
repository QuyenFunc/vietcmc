FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .

# Expose port
EXPOSE 5001

# Run server
CMD ["python", "server.py"]

