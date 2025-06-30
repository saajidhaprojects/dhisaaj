# Minimal build script for testing

Write-Host "Building minimal test application..."

# Create virtual environment
if (Test-Path "test_venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force "test_venv"
}

Write-Host "Creating new virtual environment..."
python -m venv test_venv

# Activate virtual environment
.\test_venv\Scripts\Activate.ps1

Write-Host "Installing minimal dependencies..."
pip install PyQt5

# Clean build directories
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Build using test setup
Write-Host "Building test application..."
python test_setup.py build

if (-not (Test-Path "dist")) {
    Write-Host "Build failed!"
    exit 1
}

Write-Host "Build successful!"
Write-Host "Test application built successfully in dist directory"

# Clean up
Write-Host "Cleaning up..."
Deactivate

Write-Host "Press any key to continue..."
Read-Host
