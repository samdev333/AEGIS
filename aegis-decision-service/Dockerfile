# A.E.G.I.S. Decision Service - Production Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY runbooks/ ./runbooks/

# Create non-root user
RUN useradd -m -u 1000 aegis && \
    chown -R aegis:aegis /app

USER aegis

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/health').raise_for_status()"

# Expose port
EXPOSE $PORT

# Run uvicorn
CMD uvicorn src.aegis_service.main:app --host 0.0.0.0 --port $PORT --workers 2
