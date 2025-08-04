@echo off
REM Holehe Web Interface Run Script for Windows

echo ========================================
echo     Starting Holehe Web Interface
echo ========================================

REM Check if virtual environment exists
if not exist venv (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify Python location
echo Python location: 
where python

REM Check if all required files exist
if not exist app.py (
    echo Error: app.py not found!
    pause
    exit /b 1
)

if not exist requirements.txt (
    echo Error: requirements.txt not found!
    pause
    exit /b 1
)

if not exist templates (
    echo Error: templates directory not found!
    echo Please make sure the templates directory exists with index.html
    pause
    exit /b 1
)

if not exist holehe_source (
    echo Error: holehe_source directory not found!
    echo The Holehe source code should be automatically downloaded during setup.
    echo Please run setup.bat again.
    pause
    exit /b 1
)

REM Test critical imports
echo Testing imports...
python -c "import sys, os; sys.path.insert(0, os.path.join('.', 'holehe_source')); from holehe.core import import_submodules; import httpx; import trio; import flask; print('✓ All critical imports successful')"

if %errorlevel% neq 0 (
    echo Import test failed. Please run setup.bat again.
    pause
    exit /b 1
)

REM Start the application
echo Starting Holehe Web Interface...
echo The web interface will be available at: http://localhost:5001
echo Press Ctrl+C to stop the server
echo.

python app.py --host 0.0.0.0 --port 5001

pause