# Build script for Dhivehi Dictation System using cx_Freeze

Write-Host "Building Dhivehi Dictation System with cx_Freeze..."

# Create virtual environment
if (Test-Path "cxfreeze_venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force "cxfreeze_venv"
}

Write-Host "Creating new virtual environment..."
python -m venv cxfreeze_venv

# Activate virtual environment
.\cxfreeze_venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Clean build directories
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Build using setup.py
Write-Host "Building application..."
python setup.py build

if (-not (Test-Path "dist")) {
    Write-Host "Build failed!"
    exit 1
}

Write-Host "Build successful!"
Write-Host "Application built successfully in dist directory"

# Clean up
Write-Host "Cleaning up..."
Deactivate

Write-Host "Press any key to continue..."
Read-Host
