# Alternative PowerShell launcher for the dashboard
# Use this if run_dashboard.bat has issues

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Stock Pipeline Desktop Dashboard" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

# Check if PyQt6 is installed
Write-Host "Checking dependencies..." -ForegroundColor Green
$pyqt6Check = & python -c "import PyQt6" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "PyQt6 not found. Installing dependencies..." -ForegroundColor Yellow
    Write-Host ""
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Launch dashboard
Write-Host ""
Write-Host "Launching dashboard..." -ForegroundColor Green
Write-Host ""

python dashboard\main.py

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Dashboard exited with error code $LASTEXITCODE" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
}

