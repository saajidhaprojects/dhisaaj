from cx_Freeze import setup, Executable
import sys
import os
import PyQt5
import transformers
import torch

# Get the directory containing PyQt5
pyqt5_dir = os.path.dirname(PyQt5.__file__)

# Get transformers and torch data files
transformers_dir = os.path.dirname(transformers.__file__)
torch_dir = os.path.dirname(torch.__file__)

build_exe_options = {
    "packages": [
        "PyQt5",
        "transformers",
        "torch",
        "numpy",
        "scipy",
        "soundfile"
    ],
    "excludes": [],
    "include_files": [
        (os.path.join(pyqt5_dir, "Qt5", "plugins"), "Qt5\plugins"),
        (os.path.join(pyqt5_dir, "Qt5", "translations"), "Qt5\translations"),
        (os.path.join(transformers_dir, "models"), "transformers\models"),
        (os.path.join(torch_dir, "lib"), "torch\lib"),
    ],
    "include_msvcr": True
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Transformers Test",
    version="1.0",
    description="Test Application with Transformers and Torch",
    options={"build_exe": build_exe_options},
    executables=[Executable("test_transformers.py", base=base)]
)
