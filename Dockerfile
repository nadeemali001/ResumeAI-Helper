# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create user for better permissions
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific versions for stability
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R streamlit:streamlit /app && \
    chmod -R 755 /app

# Create necessary directories with proper permissions
RUN mkdir -p /tmp/streamlit && \
    chown -R streamlit:streamlit /tmp/streamlit && \
    mkdir -p /home/streamlit/.streamlit && \
    chown -R streamlit:streamlit /home/streamlit

# Switch to streamlit user
USER streamlit

# Expose port 7860 (required for Hugging Face Spaces)
EXPOSE 7860

# Set environment variables for Hugging Face Spaces
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/huggingface

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:7860/_stcore/health

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"] 