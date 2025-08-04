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

# Verify Python and pip are from venv
echo "Python location: $(which python)"
echo "Python version: $(python --version)"

# Check if all required files exist
if [ ! -f "run.py" ]; then
    echo "Error: run.py not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

if [ ! -d "holehe_web/templates" ]; then
    echo "Error: templates directory not found!"
    echo "Please make sure the holehe_web/templates directory exists with index.html"
    exit 1
fi

if [ ! -d "holehe_source" ]; then
    echo "Error: holehe_source directory not found!"
    echo "The Holehe source code should be automatically downloaded during setup."
    echo "Please run setup.sh again."
    exit 1
fi

# Test critical imports
echo "Testing imports..."
python -c "from holehe_web import create_app; print('✓ App factory import successful')"

if [ $? -ne 0 ]; then
    echo "Import test failed. Please run setup.sh again."
    exit 1
fi

# Find an open port
port=5001
echo "Searching for an open port starting at $port..."

while true; do
    if ! lsof -i:$port > /dev/null; then
        echo "Port $port is available."
        break
    else
        echo "Port $port is in use."
        port=$((port+1))
    fi
done

# Start the application
echo "Starting Holehe Web Interface..."
echo "The web interface will be available at: http://localhost:$port"
echo "Press Ctrl+C to stop the server"
echo ""

python run.py --host 0.0.0.0 --port $port
