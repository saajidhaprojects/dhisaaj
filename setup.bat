@echo off
echo Setting up Dhivehi Dictation System...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b 1
)

:: Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install dependencies
if not exist requirements.txt (
    echo requirements.txt not found!
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

:: Create model directory
if not exist model (
    mkdir model
    echo Add your Wav2Vec2 model files to this directory > model\README.txt
)

:: Create build directory
if not exist build (
    mkdir build
)

:: Create desktop shortcut
echo Creating desktop shortcut...
set "SHORTCUT_NAME=%USERPROFILE%\Desktop\Dhivehi Dictation.lnk"
set "TARGET_FILE=%CD%\Dhivehi Dictation.exe"

powershell -Command "^$WshShell = New-Object -comObject WScript.Shell; ^$Shortcut = ^$WshShell.CreateShortcut('%SHORTCUT_NAME%'); ^$Shortcut.TargetPath = '%TARGET_FILE%'; ^$Shortcut.Save()"

echo Setup complete!
echo You can now run build_all.bat to create the executable.
pause
