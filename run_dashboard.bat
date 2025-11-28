@echo off
)
    pause
    echo Error: Dashboard exited with error code %errorlevel%
    echo.
if errorlevel 1 (
REM Keep window open if there was an error

python dashboard\main.py

echo.
echo Launching dashboard...
echo.
REM Launch dashboard

)
    )
        exit /b 1
        pause
        echo Error: Failed to install dependencies
        echo.
    if errorlevel 1 (
    pip install -r requirements.txt
    echo PyQt6 not found. Installing dependencies...
    echo.
if errorlevel 1 (
python -c "import PyQt6" 2>NUL
REM Check if PyQt6 is installed

call .venv\Scripts\activate.bat
echo Activating virtual environment...
REM Activate virtual environment

)
    exit /b 1
    pause
    echo   pip install -r requirements.txt
    echo   .venv\Scripts\activate
    echo   python -m venv .venv
    echo Please create virtual environment first:
    echo Error: Virtual environment not found!
if not exist ".venv\Scripts\activate.bat" (
REM Check if virtual environment exists

echo.
echo ====================================
echo Stock Pipeline Desktop Dashboard
echo ====================================

REM Optimized for Windows with PyQt6
REM Stock Pipeline Desktop Dashboard Launcher

