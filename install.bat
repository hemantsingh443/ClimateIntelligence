@echo off
echo Installing Climate Intelligence Application...

REM Check if Python 3.12.3 is installed
python --version 2>nul | findstr /C:"Python 3.12.3" >nul
if errorlevel 1 (
    echo Python 3.12.3 is not installed.
    echo Please install Python 3.12.3 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip and install setuptools
python -m pip install --upgrade pip setuptools wheel

REM Install requirements
python -m pip install -r requirements.txt

REM Install the package in development mode
python -m pip install -e .

echo Installation completed!
echo To run the application, use: streamlit run app.py
pause 