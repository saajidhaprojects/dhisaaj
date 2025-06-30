import sys
import os
from cx_Freeze import setup, Executable
import PyQt5

# Get the directory containing PyQt5
pyqt5_dir = os.path.dirname(PyQt5.__file__)

build_exe_options = {
    "packages": ["PyQt5"],
    "excludes": [],
    "include_files": [
        (os.path.join(pyqt5_dir, "Qt5", "plugins"), "Qt5\plugins"),
        (os.path.join(pyqt5_dir, "Qt5", "translations"), "Qt5\translations")
    ],
    "include_msvcr": True
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Test App",
    version="1.0",
    description="Minimal Test Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("test_app.py", base=base)]
)
