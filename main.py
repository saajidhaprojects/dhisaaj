import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
import sounddevice as sd
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import webrtcvad
import queue
import tempfile
import soundfile as sf

class AudioProcessor(QThread):
    transcription_update = pyqtSignal(str)
    
    def __init__(self, processor, model):
        super().__init__()
        self.processor = processor
        self.model = model
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
        
    def run(self):
        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_queue.put(indata.copy())

        stream = sd.InputStream(
            channels=1,
            samplerate=16000,
            callback=audio_callback
        )
        
        with stream:
            while self.is_recording:
                try:
                    audio_data = self.audio_queue.get()
                    self.process_audio(audio_data)
                except KeyboardInterrupt:
                    break

    def process_audio(self, audio_data):
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
            
        chunk_size = 16000
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            if len(chunk) > 0:
                transcription = self.transcribe_chunk(chunk)
                self.transcription_update.emit(transcription)

    def transcribe_chunk(self, audio_chunk):
        input_values = self.processor(audio_chunk, sampling_rate=16000, return_tensors="pt").input_values
        logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        return self.processor.decode(predicted_ids[0])

class DhivehiDictationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dhivehi Dictation System")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.setup_dark_theme()
        self.audio_processor = None

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Text area for transcription
        self.text_area = QTextEdit()
        self.text_area.setFont(QFont("Arial", 12))
        layout.addWidget(self.text_area)

        # Control buttons
        button_layout = QVBoxLayout()
        
        self.load_model_btn = QPushButton("Load Model")
        self.load_model_btn.clicked.connect(self.load_model)
        button_layout.addWidget(self.load_model_btn)

        self.start_btn = QPushButton("Start Dictation")
        self.start_btn.clicked.connect(self.start_dictation)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Dictation")
        self.stop_btn.clicked.connect(self.stop_dictation)
        button_layout.addWidget(self.stop_btn)

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

    def load_model(self):
        model_dir, _ = QFileDialog.getExistingDirectory(
            self, "Select Model Directory", "model", QFileDialog.ShowDirsOnly
        )
        if model_dir:
            try:
                # Check if required model files exist
                required_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
                missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_dir, f))]
                
                if missing_files:
                    QMessageBox.critical(self, "Error", f"Missing required model files: {', '.join(missing_files)}")
                    return

                self.processor = Wav2Vec2Processor.from_pretrained(model_dir)
                self.model = Wav2Vec2ForCTC.from_pretrained(model_dir)
                QMessageBox.information(self, "Success", "Model loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading model: {str(e)}")

    def start_dictation(self):
        if not hasattr(self, 'processor') or not hasattr(self, 'model'):
            QMessageBox.warning(self, "Warning", "Please load a model first!")
            return
            
        if self.audio_processor and self.audio_processor.isRunning():
            return
            
        self.audio_processor = AudioProcessor(self.processor, self.model)
        self.audio_processor.transcription_update.connect(self.update_text)
        self.audio_processor.is_recording = True
        self.audio_processor.start()

    def stop_dictation(self):
        if self.audio_processor:
            self.audio_processor.is_recording = False
            self.audio_processor.wait()
            self.audio_processor = None

    def update_text(self, text):
        self.text_area.append(text)

    def closeEvent(self, event):
        if self.audio_processor and self.audio_processor.isRunning():
            self.audio_processor.is_recording = False
            self.audio_processor.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DhivehiDictationApp()
    window.show()
    sys.exit(app.exec_())
