FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for document processing
RUN mkdir -p /app/incoming /app/processed /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Create non-root user
RUN useradd -m -u 1000 etl_worker && \
    chown -R etl_worker:etl_worker /app

USER etl_worker

# Run the ETL worker
CMD ["python", "-m", "etl_worker", "--watch", "/app/incoming"] 