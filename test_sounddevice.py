import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget)
import sounddevice as sd
import numpy as np

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sounddevice Test")
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        test_button = QPushButton("Test Audio")
        test_button.clicked.connect(self.test_audio)
        layout.addWidget(test_button)

    def test_audio(self):
        try:
            print("Testing audio input...")
            sd.default.samplerate = 44100
            sd.default.channels = 1
            print(f"Default device: {sd.default.device}")
            print(f"Available devices: {sd.query_devices()}")
        except Exception as e:
            print(f"Error testing audio: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())
