# PA Co-Pilot Backend Startup Script
# Starts the FastAPI backend server on port 8000

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting PA Co-Pilot Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting backend server on http://localhost:8000" -ForegroundColor Yellow
Write-Host "API endpoints will be available at http://localhost:8000/api/*" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

