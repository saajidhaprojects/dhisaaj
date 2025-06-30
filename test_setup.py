from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": ["PyQt5"],
    "excludes": [],
    "include_files": [],
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
