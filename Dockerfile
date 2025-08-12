# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for building Python packages + git + inotify
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    ca-certificates openssl curl \
    git inotify-tools \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY schema.prisma ./schema.prisma
RUN pip install --no-cache-dir "prisma==0.12.*"

# --- prisma debug (unchanged) ---
RUN python - <<'PY'
from prisma.binaries import platform, BINARY_VERSION
print("Platform:", platform())
print("Engine commit:", BINARY_VERSION)
PY

COPY schema.prisma .
ENV PRISMA_PY_BINARY_TARGETS=debian-openssl-3.0.x
RUN rm -rf /root/.cache/prisma && prisma generate

# --- add watcher + entrypoint ---
COPY auto-commit.sh /app/auto-commit.sh
COPY entrypoint.sh  /app/entrypoint.sh
RUN chmod +x /app/auto-commit.sh /app/entrypoint.sh

# Provide sane defaults; override at 'docker run'
ENV WATCH_DIR=/app
ENV GIT_BRANCH=main

# Start via entrypoint (spawns watcher + your app)
ENTRYPOINT ["/app/entrypoint.sh"]
