@echo off
REM Stock Pipeline Desktop Dashboard Launcher
REM Optimized for Windows with PyQt6

echo.
echo ====================================
echo Stock Pipeline Desktop Dashboard
echo ====================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please create virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if PyQt6 is installed
python -c "import PyQt6" 2>NUL
if errorlevel 1 (
    echo.
    echo PyQt6 not found. Installing dependencies...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Error: Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
)

REM Launch dashboard
echo.
echo Launching dashboard...
echo.

python dashboard\main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Error: Dashboard exited with error code %errorlevel%
    echo.
    pause
)

