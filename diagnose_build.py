import os
import sys
import subprocess
import pkg_resources

def check_python_environment():
    print("\nPython Environment Check:")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {os.path.dirname(sys.executable)}")

def check_installed_packages():
    print("\nInstalled Packages:")
    for dist in pkg_resources.working_set:
        print(f"{dist.project_name}=={dist.version}")

def check_pyinstaller():
    print("\nPyInstaller Version Check:")
    try:
        import PyInstaller
        print(f"PyInstaller Version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not installed")

def test_pyinstaller():
    print("\nTesting PyInstaller with simple script...")
    test_script = "test_script.py"
    with open(test_script, 'w') as f:
        f.write("""
import sys
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Hello World")
label.show()
sys.exit(app.exec_())
""")

    try:
        subprocess.run(['pyinstaller', '--onefile', '--windowed', '--name', 'TestApp', test_script], check=True)
        print("\nPyInstaller test successful!")
    except subprocess.CalledProcessError as e:
        print(f"\nPyInstaller test failed: {e}")
    finally:
        os.remove(test_script)

def main():
    print("Running Build Diagnostics...")
    check_python_environment()
    check_installed_packages()
    check_pyinstaller()
    test_pyinstaller()

if __name__ == '__main__':
    main()
