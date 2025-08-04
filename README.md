# Holehe Web Interface

A modern web interface for the [Holehe](https://github.com/megadose/holehe) email OSINT tool, designed with the same style and features as the Sherlock web interface.

![Holehe Web Interface](https://img.shields.io/badge/Status-Ready-green) ![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-red)

## Overview

Holehe Web Interface provides a user-friendly web-based frontend for the Holehe email investigation tool. It allows users to check if an email address is registered on various websites and services through an intuitive web interface.

### Features

- **Modern UI**: Clean, responsive design inspired by the Sherlock web interface
- **Real-time Progress**: Live progress updates during email searches
- **Comprehensive Results**: Detailed breakdown of found accounts, rate limits, and errors
- **PDF Reports**: Generate and download PDF reports of search results
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Filtering**: Filter results by status (found, not found, rate limited, errors)
- **Responsive Design**: Mobile-friendly interface

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Quick Setup

#### Linux/macOS

1. Clone or download this repository
2. Navigate to the project directory
3. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

#### Windows

1. Clone or download this repository
2. Navigate to the project directory
3. Run the setup script:

```cmd
setup.bat
```

### Manual Installation

If you prefer manual installation:

1. Create a virtual environment:
```bash
python3 -m venv venv  # Linux/macOS
python -m venv venv   # Windows
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Web Interface

#### Linux/macOS
```bash
./run.sh
```

#### Windows
```cmd
run.bat
```

#### Manual Start
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat # Windows

# Start the application
python app.py
```

### Accessing the Interface

1. Open your web browser
2. Navigate to `http://localhost:5001`
3. Enter an email address to investigate
4. View results in real-time

### Configuration Options

You can customize the server settings by passing command-line arguments:

```bash
python app.py --host 0.0.0.0 --port 5001 --debug
```

Options:
- `--host`: Host to bind the server to (default: 0.0.0.0)
- `--port`: Port to run the server on (default: 5001)
- `--debug`: Enable debug mode

## How It Works

1. **Email Validation**: The interface validates the entered email format
2. **Module Loading**: Holehe modules are dynamically loaded for various websites
3. **Concurrent Checking**: Multiple websites are checked simultaneously using async operations
4. **Real-time Updates**: Progress and status updates are provided via AJAX
5. **Result Processing**: Results are categorized and displayed with filtering options
6. **PDF Generation**: Comprehensive reports can be generated and downloaded

## Results Categories

- **✅ Found**: Email is registered on the website
- **❌ Not Found**: Email is not registered on the website  
- **⚠️ Rate Limited**: Request was rate limited by the website
- **🚫 Error**: An error occurred during the check

## Project Structure

```
holehe-web-interface/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.sh              # Linux/macOS setup script
├── setup.bat             # Windows setup script
├── run.sh                # Linux/macOS run script
├── run.bat               # Windows run script
├── templates/
│   └── index.html        # Main web interface template
├── holehe_source/        # Holehe source code (auto-cloned)
└── venv/                 # Virtual environment (created during setup)
```

## API Endpoints

- `GET /`: Main interface page
- `POST /search`: Start a new email search
- `GET /status/<search_id>`: Get search progress and status
- `GET /results/<search_id>`: Get search results
- `GET /download/<search_id>`: Download PDF report

## Dependencies

- **Flask**: Web framework
- **httpx**: HTTP client for async requests
- **trio**: Async library for concurrent operations
- **reportlab**: PDF generation
- **beautifulsoup4**: HTML parsing
- **termcolor**: Terminal colors
- **colorama**: Cross-platform terminal colors

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port using `--port` argument
2. **Module import errors**: Ensure the holehe_source directory exists and contains the Holehe code
3. **Permission errors**: Make sure scripts have executable permissions on Linux/macOS

### Virtual Environment Issues

If you encounter virtual environment issues:

```bash
# Remove existing venv
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Run setup again
./setup.sh  # Linux/macOS
setup.bat   # Windows
```

## Security Considerations

- The web interface runs on localhost by default
- No sensitive data is stored permanently
- Search results are temporarily cached in memory
- PDF reports are created in system temporary directory

## Contributing

This web interface is designed to complement the original Holehe tool. For issues with the core Holehe functionality, please refer to the [original Holehe repository](https://github.com/megadose/holehe).

## License

This web interface follows the same licensing as the original Holehe project. Please refer to the [original repository](https://github.com/megadose/holehe) for license information.

## Acknowledgments

- Thanks to [megadose](https://github.com/megadose) for the original Holehe tool
- Inspired by the Sherlock web interface design
- Built with modern web technologies for optimal user experience

## Support

For issues specifically related to this web interface:
1. Check the troubleshooting section
2. Ensure all dependencies are properly installed
3. Verify Python version compatibility (3.7+)

For issues with the core Holehe functionality, please refer to the [original Holehe repository](https://github.com/megadose/holehe).