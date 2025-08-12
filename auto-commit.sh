#!/bin/bash
WATCH_DIR=/app   # Path inside the container
GIT_REPO=https://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@github.com/username/repo.git

cd $WATCH_DIR || exit 1

while inotifywait -r -e modify,create,delete,move .; do
    git add .
    git commit -m "Auto commit $(date '+%Y-%m-%d %H:%M:%S')"
    git push $GIT_REPO main
done