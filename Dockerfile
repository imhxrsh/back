# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    gcc \
    g++ \
    # PDF processing dependencies
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    # Image processing dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Additional system libraries
    libpq-dev \
    libffi-dev \
    libssl-dev \
    # Utilities
    curl \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user early (before copying files)
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Copy requirements first for better layer caching
COPY --chown=appuser:appuser requirements.txt .

# Upgrade pip and install Python packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper ownership
RUN mkdir -p /app/processed_data \
    /app/backups \
    /app/models \
    /app/logs \
    /app/agent_workspace \
    /app/agents/agent_workspace \
    && chown -R appuser:appuser /app

# Switch to non-root user before copying application code
USER appuser

# Copy application code (this should come after switching user)
COPY --chown=appuser:appuser . .

# Ensure the main application module exists and create it if missing
RUN if [ ! -f "/app/app/main.py" ]; then \
    echo "Warning: app/main.py not found. Creating a basic FastAPI app..." && \
    mkdir -p /app/app && \
    echo 'from fastapi import FastAPI\nfrom fastapi.responses import JSONResponse\n\napp = FastAPI(title="BlueCore Backend", version="1.0.0")\n\n@app.get("/")\nasync def root():\n    return {"message": "BlueCore Backend is running"}\n\n@app.get("/api/health")\nasync def health_check():\n    return JSONResponse(content={"status": "healthy"}, status_code=200)' > /app/app/main.py && \
    touch /app/app/__init__.py; \
    fi

# Set proper permissions for all created directories and files
USER root
RUN chmod -R 755 /app && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]