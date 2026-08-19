FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Configure Streamlit
RUN mkdir -p /root/.streamlit && \
    echo '[server]' > /root/.streamlit/config.toml && \
    echo 'headless = true' >> /root/.streamlit/config.toml && \
    echo 'port = 8501' >> /root/.streamlit/config.toml && \
    echo '[logger]' >> /root/.streamlit/config.toml && \
    echo 'level = "info"' >> /root/.streamlit/config.toml

# Run application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
