#!/bin/bash
# This script attempts to apply database migrations using Flask-Migrate,
# retrying on failure until successful, then starts the Gunicorn server.

while true; do
    flask db upgrade
    if [ $? -eq 0 ]; then
        break
    fi
    echo "Database migration failed, retrying in 5 seconds..."
    sleep 5
done
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app