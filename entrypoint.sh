#!/bin/bash

# Make sure SECRET_KEY is set
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="production-key-for-smartreminder-$(date +%s)"
    echo "WARNING: Setting a random SECRET_KEY. This will be lost on container restart."
fi

# Initialize the application with init_db function instead of importing db
python -c "from app import app, init_db; print('Application initialized')"

# Start the Flask application with Gunicorn
exec gunicorn --bind 0.0.0.0:${PORT:-8080} "app:app"