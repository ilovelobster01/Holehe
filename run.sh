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

if [ ! -d "holehe_source" ]; then
    echo "Error: holehe_source directory not found!"
    echo "The Holehe source code should be automatically downloaded during setup."
    echo "Please run setup.sh again."
    exit 1
fi

# Test critical imports
echo "Testing imports..."
python -c "
import sys, os
sys.path.insert(0, os.path.join('.', 'holehe_source'))
try:
    from holehe.core import import_submodules
    import httpx
    import trio
    import flask
    print('✓ All critical imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
    print('Please run setup.sh again to reinstall dependencies.')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "Import test failed. Please run setup.sh again."
    exit 1
fi

# Start the application
echo "Starting Holehe Web Interface..."
echo "The web interface will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py --host 0.0.0.0 --port 5001