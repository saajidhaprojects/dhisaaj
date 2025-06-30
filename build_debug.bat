@echo off
echo Building Dhivehi Dictation System with debug information...

:: Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check Python version
echo Checking Python version...
python --version

:: Check pip version
echo Checking pip version...
pip --version

:: Check installed packages
echo Checking installed packages...
pip list

:: Create build directory
if not exist build_debug mkdir build_debug

echo.
echo Starting detailed build process...
echo.

:: Build the application with detailed output
pyinstaller --noconfirm --onefile --windowed --name "Dhivehi Dictation" --icon=icon.ico main.py --log-level DEBUG > build_debug\build.log 2>&1

echo.
echo Build process completed.
echo.

echo Checking build results...
if not exist dist\Dhivehi Dictation.exe (
    echo Build failed! Detailed log saved to build_debug\build.log
    echo.
    echo Last 50 lines of build log:
    type build_debug\build.log | findstr /n "" | findstr /r /c:"[0-9][0-9]*:.*ERROR" /c:"[0-9][0-9]*:.*WARNING" /c:"[0-9][0-9]*:.*Failed"
    pause
    exit /b 1
)

echo Build successful!
echo.
echo Application files:
echo - Main executable: Dhivehi Dictation.exe
echo - Build log: build_debug\build.log
echo.
echo You can now run the application using any of these methods:
echo 1. Double-click "Dhivehi Dictation.exe"
echo 2. Run "start_dhivehi_dictation.bat"
echo 3. Use the desktop shortcut
pause
