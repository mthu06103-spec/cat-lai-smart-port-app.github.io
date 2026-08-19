FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models __init__.py files
RUN mkdir -p models algorithms && \
    touch models/__init__.py && \
    touch algorithms/__init__.py

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
