# Build script for Dhivehi Dictation System

Write-Host "Building Dhivehi Dictation System..."

# Create virtual environment
if (Test-Path "robust_venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force "robust_venv"
}

Write-Host "Creating new virtual environment..."
python -m venv robust_venv

# Activate virtual environment
.\robust_venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
pip install --upgrade pip

Write-Host "Installing all dependencies..."
$deps = @(
    "PyQt5==5.15.9",
    "pyinstaller==4.10",
    "numpy==1.21.6",
    "sounddevice==0.4.6",
    "transformers==4.30.2",
    "torch==2.0.1",
    "soundfile==0.12.1",
    "webrtcvad==2.0.10",
    "scipy==1.7.3"
)

foreach ($dep in $deps) {
    pip install $dep
}

# Clean build directories
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Build using spec file
Write-Host "Building using spec file..."
pyinstaller --noconfirm --onefile --windowed dhivehi_dictation.spec

if (-not (Test-Path "dist\Dhivehi Dictation.exe")) {
    Write-Host "Build failed!"
    exit 1
}

Write-Host "Build successful!"
Write-Host "Running the application..."
Start-Process -FilePath "dist\Dhivehi Dictation.exe"

# Clean up
Write-Host "Cleaning up..."
Deactivate

Write-Host "Press any key to continue..."
Read-Host
