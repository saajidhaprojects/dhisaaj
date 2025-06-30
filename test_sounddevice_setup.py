from cx_Freeze import setup, Executable
import sys
import os
import PyQt5
import sounddevice

# Get the directory containing PyQt5
pyqt5_dir = os.path.dirname(PyQt5.__file__)

# Get sounddevice data files
sounddevice_dir = os.path.dirname(sounddevice.__file__)

build_exe_options = {
    "packages": ["PyQt5", "sounddevice", "numpy"],
    "excludes": [],
    "include_files": [
        (os.path.join(pyqt5_dir, "Qt5", "plugins"), "Qt5\plugins"),
        (os.path.join(pyqt5_dir, "Qt5", "translations"), "Qt5\translations"),
        (os.path.join(sounddevice_dir, "_sounddevice_data", "portaudio-binaries"), "_sounddevice_data\portaudio-binaries")
    ],
    "include_msvcr": True
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Sounddevice Test",
    version="1.0",
    description="Test Application with Sounddevice",
    options={"build_exe": build_exe_options},
    executables=[Executable("test_sounddevice.py", base=base)]
)
