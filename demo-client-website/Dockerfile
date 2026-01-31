# Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Node dependencies and build frontend
RUN npm ci
RUN npm run build

# Verify build output
RUN echo "=== Checking build output ===" && ls -la dist || echo "dist not found"

# Expose the port the app runs on
EXPOSE 5000

# Start the application
CMD ["python", "backend/server.py"]
