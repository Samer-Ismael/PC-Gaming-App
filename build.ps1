# PowerShell build script for Monitor.exe
Write-Host "Building Monitor.exe..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please make sure Python is installed and in your PATH." -ForegroundColor Red
    exit 1
}

# Check if PyInstaller is installed
try {
    python -c "import PyInstaller" 2>&1 | Out-Null
    Write-Host "PyInstaller is installed." -ForegroundColor Green
} catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Starting build process..." -ForegroundColor Cyan
Write-Host ""

# Build using spec file
python -m PyInstaller Monitor.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Build successful!" -ForegroundColor Green
Write-Host "Executable is in: dist\Monitor.exe" -ForegroundColor Green
Write-Host ""

