import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QWidget, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
import sounddevice as sd
import numpy as np

class MinimalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Dhivehi Dictation")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.setup_dark_theme()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Text area
        self.text_area = QTextEdit()
        self.text_area.setFont(QFont("Arial", 12))
        layout.addWidget(self.text_area)

        # Test buttons
        button_layout = QVBoxLayout()
        
        test_button = QPushButton("Test Audio")
        test_button.clicked.connect(self.test_audio)
        button_layout.addWidget(test_button)

        layout.addLayout(button_layout)

    def setup_dark_theme(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def test_audio(self):
        try:
            # Test audio input
            duration = 5  # seconds
            fs = 16000
            print(f"Testing audio input for {duration} seconds...")
            
            def callback(indata, frames, time, status):
                if status:
                    print(status)
                # Just print the first value of each frame
                print(f"Audio data: {indata[0][0]:.2f}")

            with sd.InputStream(
                channels=1,
                samplerate=fs,
                callback=callback
            ):
                self.text_area.append(f"Testing audio for {duration} seconds...")
                sd.sleep(int(duration * 1000))
                
            QMessageBox.information(self, "Success", "Audio test completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Audio test failed: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MinimalApp()
    window.show()
    sys.exit(app.exec_())
