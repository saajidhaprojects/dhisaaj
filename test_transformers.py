import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit)
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import torch

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transformers Test")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        test_button = QPushButton("Test Model")
        test_button.clicked.connect(self.test_model)
        layout.addWidget(test_button)

    def test_model(self):
        try:
            self.text_area.append("Loading model...")
            tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
            model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
            self.text_area.append("Model loaded successfully!")
        except Exception as e:
            self.text_area.append(f"Error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())
