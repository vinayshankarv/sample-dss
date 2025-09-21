# Review II Scraper Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY review2/ ./review2/
COPY config.yml .

# Create output directory
RUN mkdir -p review2/data

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app
USER scraper

# Default command
CMD ["python", "review2/scraper/run_scraper.py", "--config", "config.yml", "--mode", "dry-run"]