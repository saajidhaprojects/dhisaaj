@echo off
echo Testing build process...

:: Create virtual environment
echo Creating virtual environment...
python -m venv test_venv

echo Activating virtual environment...
call test_venv\Scripts\activate.bat

:: Install minimal dependencies
echo Installing minimal dependencies...
pip install PyQt5

:: Test simple build
echo Testing simple build...
pyinstaller --noconfirm --onefile --windowed --name "TestApp" test_app.py

:: Check build results
if not exist dist\TestApp.exe (
    echo Simple build failed!
    pause
    exit /b 1
)

echo Simple build successful!
echo.
echo Testing complex build with all dependencies...

:: Install all dependencies
echo Installing all dependencies...
pip install -r requirements.txt

:: Test complex build
echo Testing complex build...
pyinstaller --noconfirm --onefile --windowed --name "Dhivehi Dictation" --icon=icon.ico main.py

:: Check build results
if not exist dist\Dhivehi Dictation.exe (
    echo Complex build failed!
    pause
    exit /b 1
)

echo All builds successful!
echo.
echo You can now run the test application:
start dist\TestApp.exe
pause
