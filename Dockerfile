# Use Python 3.11 slim image
FROM python:3.13-slim

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY schema.prisma ./schema.prisma
RUN prisma generate

# Copy the rest of your app
COPY . .

# Run the application
CMD ["python", "main.py"]
