# SecureEye Startup Script for PowerShell
Write-Host "Starting SecureEye Dashboard..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+ and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start Backend Server
Write-Host "Starting backend server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "backend\app.py" -WindowStyle Normal -WorkingDirectory (Get-Location)

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Web Server
Write-Host "Starting web server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8000" -WindowStyle Normal -WorkingDirectory (Get-Location)

# Wait for servers to start
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Servers should be starting..." -ForegroundColor Green
Write-Host "Dashboard URL: http://localhost:8000/home.html" -ForegroundColor Cyan
Write-Host "Debug URL: http://localhost:8000/debug.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening debug page in browser..." -ForegroundColor Yellow

# Open debug page
try {
    Start-Process "http://localhost:8000/debug.html"
} catch {
    Write-Host "Could not open browser automatically. Please open http://localhost:8000/debug.html manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit this script (servers will continue running)..." -ForegroundColor Gray
Read-Host
