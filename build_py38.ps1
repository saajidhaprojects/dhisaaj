# Build script for Dhivehi Dictation System using Python 3.8

Write-Host "Building Dhivehi Dictation System with Python 3.8..."

# Create virtual environment
if (Test-Path "venv_py38") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force "venv_py38"
}

Write-Host "Creating new virtual environment with Python 3.8..."
python -m venv venv_py38 --python=python3.8

# Activate virtual environment
.\venv_py38\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_py38.txt

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
