#!/bin/bash

echo "Starting API Gateway..."

# Wait a bit for services to be ready
sleep 2

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
