#!/bin/bash

# Holehe Web Interface Run Script for Linux/macOS

echo "========================================"
echo "    Starting Holehe Web Interface"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup.sh first to create the virtual environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if all required files exist
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

if [ ! -d "templates" ]; then
    echo "Error: templates directory not found!"
    echo "Please make sure the templates directory exists with index.html"
    exit 1
fi

# Start the application
echo "Starting Holehe Web Interface..."
echo "The web interface will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py --host 0.0.0.0 --port 5001