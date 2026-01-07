# Frontend Startup Script for Windows PowerShell
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location "frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
REACT_APP_API_URL=http://localhost:5000/api
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host ".env file created!" -ForegroundColor Green
}

# Start the development server
Write-Host "Starting React development server on http://localhost:3000..." -ForegroundColor Green
npm start
