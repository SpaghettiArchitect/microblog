#!/bin/bash
# This script attempts to apply database migrations using Flask-Migrate,
# retrying on failure until successful, then starts the Gunicorn server.
set -e

# Function to handle graceful shutdown
shutdown() {
    echo "Shutting down gracefully..."
    kill -TERM "$child" 2>/dev/null
}

trap shutdown SIGTERM SIGINT

# Database migration with retry logic
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    flask db upgrade
    if [ $? -eq 0 ]; then
        echo "Database migration successful"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Database migration failed (attempt $RETRY_COUNT/$MAX_RETRIES), retrying in 5 seconds..."
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Database migration failed after $MAX_RETRIES attempts. Exiting."
    exit 1
fi

# Determine number of workers based on CPU cores
WORKERS=${WORKERS:-$((2 * $(nproc) + 1))}
THREADS=${THREADS:-2}
WORKER_CLASS=${WORKER_CLASS:-sync}
WORKER_CONNECTIONS=${WORKER_CONNECTIONS:-1000}
TIMEOUT=${TIMEOUT:-120}
KEEPALIVE=${KEEPALIVE:-5}
MAX_REQUESTS=${MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-50}

# Start Gunicorn with optimized settings
exec gunicorn microblog:app \
    --bind :5000 \
    --workers $WORKERS \
    --threads $THREADS \
    --worker-class $WORKER_CLASS \
    --worker-connections $WORKER_CONNECTIONS \
    --timeout $TIMEOUT \
    --keep-alive $KEEPALIVE \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter $MAX_REQUESTS_JITTER \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --preload \
    --enable-stdio-inheritance \
    &

child=$!
wait "$child"