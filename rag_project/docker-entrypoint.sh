#!/bin/bash
set -e

echo "Starting SmartDocs AI Pro deployment..."

# Initialize data directories
mkdir -p /app/data/uploads /app/data/docs

# Start Flask backend in background
echo "Starting Flask backend on port 8000..."
cd /app
python backend/app.py &

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 5

# Start Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
