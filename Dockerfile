# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
# Create necessary directories
RUN mkdir -p data logs

# Create user and set permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Make startup scripts executable
RUN chmod +x start_app.py setup_telegram_sessions.py simple_session_check.py

# Run the application with session check
CMD ["python", "start_app.py"]
