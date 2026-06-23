#!/bin/sh
set -e

# Apply database migrations before starting the app.
echo "Running database migrations..."
alembic upgrade head

# Hand off to the container command (e.g. the FastAPI server).
exec "$@"
