@echo off
echo Building Minimal Application...

:: Create virtual environment
if not exist minimal_venv (
    echo Creating virtual environment...
    python -m venv minimal_venv
)

call minimal_venv\Scripts\activate.bat

echo Installing minimal dependencies...
pip install -r minimal_requirements.txt

:: Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Build with verbose output
echo Building with verbose output...
pyinstaller --noconfirm --onefile --windowed --name "Minimal Dictation" minimal_app.py --log-level DEBUG > build.log 2>&1

:: Check build results
if not exist dist\Minimal Dictation.exe (
    echo Build failed!
    echo.
    echo Build log:
    type build.log
    pause
    exit /b 1
)

echo Build successful!
echo.
echo Running the application...
start dist\Minimal Dictation.exe
pause
