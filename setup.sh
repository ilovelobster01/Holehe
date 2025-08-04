#!/bin/bash

# Holehe Web Interface Setup Script for Linux/macOS
# This script creates a virtual environment and installs dependencies

echo "========================================"
echo "    Holehe Web Interface Setup (Linux)" 
echo "========================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version detected: $python_version"

if [[ "$(printf '%s\n' "3.7" "$python_version" | sort -V | head -n1)" != "3.7" ]]; then
    echo "Error: Python 3.7 or higher is required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create templates directory
echo "Creating templates directory..."
mkdir -p templates

echo ""
echo "========================================"
echo "    Setup completed successfully!"
echo "========================================"
echo ""
echo "To start the Holehe web interface:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the application:"
echo "   python app.py"
echo ""
echo "3. Open your browser and go to:"
echo "   http://localhost:5001"
echo ""
echo "To deactivate the virtual environment later:"
echo "   deactivate"
echo ""