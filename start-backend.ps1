# Backend Startup Script for Windows PowerShell
Write-Host "Starting Backend Server..." -ForegroundColor Cyan

# Navigate to backend directory
Set-Location "backend"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your configuration." -ForegroundColor Yellow
    Write-Host "See RUN_INSTRUCTIONS.md for details." -ForegroundColor Yellow
}

# Start the server
Write-Host "Starting Flask server on http://localhost:5000..." -ForegroundColor Green
python app.py
