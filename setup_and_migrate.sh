#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install sqlalchemy-utils

# Run database setup
python scripts/setup_db.py

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Create initial data if needed
echo "Creating initial data..."
python app/initial_data.py

echo "Setup completed successfully!"
echo "You can now start the server with: .venv/bin/uvicorn app.main:app --reload"
