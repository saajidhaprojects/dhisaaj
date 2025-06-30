@echo off
echo Building Dhivehi Dictation System...

:: Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if dependencies are installed
pip list | findstr "PyQt5 transformers torch" >nul
if %errorlevel% neq 0 (
    echo Dependencies not found. Please run setup.bat to install them.
    pause
    exit /b 1
)

:: Create build directory
if not exist build mkdir build

:: Create executable
echo Creating executable...
if exist icon.ico (
    pyinstaller --noconfirm --onefile --windowed --name "Dhivehi Dictation" --icon=icon.ico main.py
) else (
    pyinstaller --noconfirm --onefile --windowed --name "Dhivehi Dictation" main.py
)

:: Check if build was successful
if not exist dist\Dhivehi Dictation.exe (
    echo Build failed! Could not find executable in dist directory.
    pause
    exit /b 1
)

:: Clean up
echo Cleaning up...
if exist build\__pycache__ rmdir /s /q build\__pycache__
if exist build\build rmdir /s /q build\build
if exist build\dhivehi_dictation.spec del build\dhivehi_dictation.spec

:: Move executable to main directory
echo Moving executable...
move dist\Dhivehi Dictation.exe .

:: Clean up dist directory
if exist dist rmdir /s /q dist

:: Create start script with proper path handling
echo @echo off > start_dhivehi_dictation.bat
echo set "CURRENT_DIR=%~dp0" >> start_dhivehi_dictation.bat
echo cd /d "%%CURRENT_DIR%%" >> start_dhivehi_dictation.bat
echo start "Dhivehi Dictation" "Dhivehi Dictation.exe" >> start_dhivehi_dictation.bat

:: Create desktop shortcut with proper path handling
echo Creating desktop shortcut...
set "SHORTCUT_NAME=%USERPROFILE%\Desktop\Dhivehi Dictation.lnk"
set "TARGET_FILE=%CD%\Dhivehi Dictation.exe"

powershell -Command "^$WshShell = New-Object -comObject WScript.Shell; ^$Shortcut = ^$WshShell.CreateShortcut('%SHORTCUT_NAME%'); ^$Shortcut.TargetPath = '%TARGET_FILE%'; ^$Shortcut.WorkingDirectory = '%CD%'; ^$Shortcut.Save()"

:: Check if shortcut was created successfully
if not exist "%SHORTCUT_NAME%" (
    echo Failed to create desktop shortcut.
)

echo Build complete!
echo.
echo Application files:
echo - Main executable: Dhivehi Dictation.exe
echo - Start script: start_dhivehi_dictation.bat
echo - Desktop shortcut: %SHORTCUT_NAME%
echo.
echo You can now run the application using any of these methods:
echo 1. Double-click "Dhivehi Dictation.exe"
echo 2. Run "start_dhivehi_dictation.bat"
echo 3. Use the desktop shortcut
pause
