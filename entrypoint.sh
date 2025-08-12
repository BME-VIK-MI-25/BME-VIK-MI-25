#!/usr/bin/env bash
set -euo pipefail

# Configure git identity if provided
if [ -n "${GIT_USER:-}" ]; then git config --global user.name  "$GIT_USER"; fi
if [ -n "${GIT_EMAIL:-}" ]; then git config --global user.email "$GIT_EMAIL"; fi

# Start watcher only if creds + repo are present
if [ -n "${GH_TOKEN:-}" ] && [ -n "${GIT_REPO:-}" ]; then
  /app/auto-commit.sh &
  echo "auto-commit: watcher started."
else
  echo "auto-commit: disabled (missing GH_TOKEN or GIT_REPO)."
fi

# Run your application in foreground
exec python /app/main.py
