# Simplified Dockerfile - Dev mode
FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Node dependencies
RUN npm install

# Build frontend
RUN npm run build

EXPOSE 5000

CMD ["python", "backend/server.py"]
