@echo off
echo Building Dhivehi Dictation System with robust error handling...

:: Create a clean virtual environment
if exist robust_venv (
    echo Removing existing virtual environment...
    rmdir /s /q robust_venv
)

:: Create new virtual environment
echo Creating new virtual environment...
python -m venv robust_venv

call robust_venv\Scripts\activate.bat

echo.
echo Upgrading pip...
pip install --upgrade pip

:: Install minimal dependencies first
echo Installing minimal dependencies...
pip install PyQt5==5.15.9 pyinstaller==4.10 numpy==1.21.6 sounddevice==0.4.6

:: Clean build directories
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Build minimal version first
echo Building minimal version...
pyinstaller --noconfirm --onefile --windowed --name "Minimal Dictation" minimal_app.py

if not exist dist\Minimal Dictation.exe (
    echo Minimal build failed!
    goto :cleanup
)

echo Minimal build successful!

:: Install remaining dependencies
echo Installing remaining dependencies...
pip install transformers==4.30.2 torch==2.0.1 soundfile==0.12.1 webrtcvad==2.0.10 scipy==1.7.3

:: Clean build directories again
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Build full version
echo Building full version...
pyinstaller --noconfirm --onefile --windowed --name "Dhivehi Dictation" main.py

if not exist dist\Dhivehi Dictation.exe (
    echo Full build failed!
    goto :cleanup
)

echo Build successful!
echo.
echo Running the application...
start dist\Dhivehi Dictation.exe

goto :end

:cleanup
echo Cleaning up...
deactivate

:end
pause
