# Dockerfile for Sci-Space Clone
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PDF processing and AI packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first (for caching)
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ .

# Railway provides PORT env variable, default to 8000
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Run application - use PORT from environment
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
