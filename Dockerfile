# Use Python 3.11 slim image
FROM python:3.12-slim

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    ca-certificates openssl curl \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY schema.prisma ./schema.prisma
RUN pip install --no-cache-dir "prisma==0.12.*" -r requirements.txt

RUN chmod +x ./auto-commit.sh  \
     && ./auto-commit.sh

# debug the intended platform/commit
RUN python - <<'PY'
from prisma.binaries import platform, BINARY_VERSION
print("Platform:", platform())
print("Engine commit:", BINARY_VERSION)
PY

COPY schema.prisma .
ENV PRISMA_PY_BINARY_TARGETS=debian-openssl-3.0.x
RUN rm -rf /root/.cache/prisma && prisma generate

# Run the application
CMD ["python", "main.py"]

