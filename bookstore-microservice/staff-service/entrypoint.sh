#!/bin/bash

echo "Starting Staff Service..."

# Wait for database
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Create migrations directory if not exists
mkdir -p /app/app/migrations
touch /app/app/migrations/__init__.py

# Create and run migrations
echo "Creating migrations..."
python manage.py makemigrations app

echo "Running migrations..."
python manage.py migrate

echo "Creating admin user..."
python manage.py create_admin || true

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
