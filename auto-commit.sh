#!/usr/bin/env bash
set -euo pipefail

: "${WATCH_DIR:=/app}"
: "${GIT_BRANCH:=main}"

cd "$WATCH_DIR"

# Expect GIT_REPO like: github.com/USERNAME/REPO.git (no scheme)
REMOTE_URL="https://${GH_TOKEN}@${GIT_REPO}"

# Ensure repo exists + remote configured
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "auto-commit: initializing git repo in $WATCH_DIR"
  git init
  git checkout -B "$GIT_BRANCH"
  git remote add origin "$REMOTE_URL"
else
  if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REMOTE_URL"
  else
    git remote add origin "$REMOTE_URL"
  fi
fi

# Optional first push
git add -A || true
if ! git diff --cached --quiet; then
  git commit -m "Initial auto-commit $(date '+%F %T')" || true
  git push -u origin "$GIT_BRANCH" || true
fi

echo "auto-commit: watching $WATCH_DIR on branch $GIT_BRANCH ..."
while inotifywait -r -e modify,create,delete,move "$WATCH_DIR"; do
  git add -A || true
  if git diff --cached --quiet; then
    continue
  fi
  git commit -m "Auto commit $(date '+%F %T')" || true
  git push origin "$GIT_BRANCH" || true
done
