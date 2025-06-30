from cx_Freeze import setup, Executable
import sys
import os

# Dependencies are automatically detected, but it might need
# fine tuning.
build_exe_options = {
    "packages": [
        "PyQt5",
        "transformers",
        "torch",
        "numpy",
        "sounddevice",
        "soundfile",
        "webrtcvad",
        "scipy"
    ],
    "excludes": [],
    "include_files": [
        ("sounddevice/_sounddevice_data/portaudio-binaries", "sounddevice/_sounddevice_data/portaudio-binaries"),
    ],
    "include_msvcr": True
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Dhivehi Dictation",
    version="1.0",
    description="Dhivehi Language Dictation System",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
