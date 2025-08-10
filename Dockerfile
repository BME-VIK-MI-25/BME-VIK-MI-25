# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    curl \
    openssl \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Prisma schema and generate client
COPY schema.prisma ./schema.prisma
RUN prisma generate

# Copy the rest of the application code
COPY . .

# Run the app
CMD ["python", "main.py"]
