#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head || echo "Migration failed (DB might not be ready yet, will retry on next restart)"

echo "Starting application..."
exec "$@"
