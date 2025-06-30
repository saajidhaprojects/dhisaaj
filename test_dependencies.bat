@echo off
echo Testing dependencies one by one...

:: Create test virtual environment
if not exist test_venv (
    echo Creating test virtual environment...
    python -m venv test_venv
)

call test_venv\Scripts\activate.bat

echo.
echo Testing PyQt5...
pip install PyQt5
pyinstaller --noconfirm --onefile --windowed --name "TestPyQt5" test_app.py
if not exist dist\TestPyQt5.exe (
    echo PyQt5 test failed
    goto :cleanup
)

echo.
echo Testing transformers...
pip install transformers
del dist\TestPyQt5.exe
pyinstaller --noconfirm --onefile --windowed --name "TestTransformers" test_app.py
if not exist dist\TestTransformers.exe (
    echo transformers test failed
    goto :cleanup
)

echo.
echo Testing torch...
pip install torch
del dist\TestTransformers.exe
pyinstaller --noconfirm --onefile --windowed --name "TestTorch" test_app.py
if not exist dist\TestTorch.exe (
    echo torch test failed
    goto :cleanup
)

echo.
echo Testing numpy...
pip install numpy
del dist\TestTorch.exe
pyinstaller --noconfirm --onefile --windowed --name "TestNumpy" test_app.py
if not exist dist\TestNumpy.exe (
    echo numpy test failed
    goto :cleanup
)

echo.
echo Testing sounddevice...
pip install sounddevice
del dist\TestNumpy.exe
pyinstaller --noconfirm --onefile --windowed --name "TestSounddevice" test_app.py
if not exist dist\TestSounddevice.exe (
    echo sounddevice test failed
    goto :cleanup
)

echo.
echo All dependencies tested successfully!

:cleanup
echo Cleaning up...
if exist dist rmdir /s /q dist
deactivate
echo.
echo Tests complete. Check the output above to see which dependency caused the failure.
pause
