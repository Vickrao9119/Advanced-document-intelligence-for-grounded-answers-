# SmartDocs AI Pro - Local Deployment Script (Windows PowerShell)

Write-Host "Starting SmartDocs AI Pro deployment..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create data directories
Write-Host "Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path data\uploads
New-Item -ItemType Directory -Force -Path data\docs

# Start Flask backend
Write-Host "Starting Flask backend on port 8000..." -ForegroundColor Green
$backend = Start-Process python -ArgumentList "backend/app.py" -PassThru -NoNewWindow

# Wait for backend to start
Start-Sleep -Seconds 5

# Start Streamlit frontend
Write-Host "Starting Streamlit frontend on port 8501..." -ForegroundColor Green
$frontend = Start-Process python -ArgumentList "-m streamlit run src/app.py" -PassThru -NoNewWindow

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow

# Wait for user input to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Process -Id $backend.Id -Force
    Stop-Process -Id $frontend.Id -Force
    Write-Host "Services stopped." -ForegroundColor Green
}
