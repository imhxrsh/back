# Use full Python 3.11 image as base (includes more system packages)
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install additional system dependencies (full Python image already has many packages)
RUN apt-get update && apt-get install -y \
    # PDF processing dependencies
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    # Additional system libraries that might not be in full image
    libpq-dev \
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

# Copy application code
COPY --chown=appuser:appuser . .

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