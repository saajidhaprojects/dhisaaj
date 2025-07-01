import sys
import queue
import logging
import pyaudio
import numpy as np
import whisper
import torch
import queue
import threading
import time
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('dictation.log')  # Log to file
    ]
)

# Set up logging for specific modules
logging.getLogger('pyaudio').setLevel(logging.ERROR)
logging.getLogger('whisper').setLevel(logging.ERROR)

# Global error handling
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, "Error", f"An unexpected error occurred: {str(exc_value)}")
    sys.exit(1)

sys.excepthook = handle_exception

class EnglishDictation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_listening = False
        
        # Initialize audio parameters with optimized values
        self.sample_rate = 16000
        self.chunk_size = 512  # Even smaller chunks for better responsiveness
        self.silence_threshold = 1000  # Lower threshold for more sensitive silence detection
        self.min_silence_duration = 0.1  # Very short silence duration
        self.last_text = ""
        self.confidence_threshold = 0.7  # Adjusted confidence threshold
        self.silence_counter = 0
        self.min_speech_duration = 0.1  # Shorter speech duration
        self.window_size = int(self.sample_rate * 1.5)  # Reduced window size
        self.slide_size = int(self.sample_rate * 0.25)  # More frequent processing
        self.max_buffer_size = int(self.sample_rate * 4)  # Limit buffer size
        
        try:
            # Initialize Whisper model with original parameters
            logging.info("Initializing Whisper model...")
            self.model = whisper.load_model("base", download_root=".")
            self.model = self.model.to('cuda' if torch.cuda.is_available() else 'cpu')
            logging.info("Whisper model loaded successfully")
            
            # Configure PyAudio with optimized settings
            logging.info("Initializing PyAudio...")
            self.audio = pyaudio.PyAudio()
            self.stream = None
            self.audio_queue = queue.Queue(maxsize=10)  # Limited queue size
            
            # Initialize sliding window buffer
            self.window_buffer = np.zeros(self.window_size, dtype=np.int16)
            self.window_index = 0
            self.current_buffer = np.array([], dtype=np.int16)
            
            # Start audio processing thread
            logging.info("Starting audio processing thread...")
            self.processing_thread = threading.Thread(target=self.process_audio_loop, daemon=True)
            self.processing_thread.start()
            logging.info("Audio processing thread started successfully")
            
        except Exception as e:
            logging.error(f"Error initializing application: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to initialize application: {str(e)}")
            # Only cleanup if we have initialized some resources
            if hasattr(self, 'processing_thread'):
                self.cleanup()
            sys.exit(1)

    def cleanup(self):
        """Clean up resources when application exits"""
        try:
            if hasattr(self, 'processing_thread') and self.processing_thread and self.processing_thread.is_alive():
                self.is_listening = False
                self.processing_thread.join()
            
            if hasattr(self, 'stream') and self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception as e:
                    logging.error(f"Error closing stream: {str(e)}", exc_info=True)
            
            if hasattr(self, 'audio') and self.audio:
                try:
                    self.audio.terminate()
                except Exception as e:
                    logging.error(f"Error terminating PyAudio: {str(e)}", exc_info=True)
            
            # Clear buffers if they exist
            if hasattr(self, 'window_buffer'):
                self.window_buffer = None
            if hasattr(self, 'current_buffer'):
                self.current_buffer = None
            if hasattr(self, 'audio_queue'):
                self.audio_queue = None
            
            logging.info("Resources cleaned up successfully")
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}", exc_info=True)

    def init_ui(self):
        try:
            # Set up main window
            self.setWindowTitle("English Speech Recognition")
            self.setGeometry(100, 100, 800, 600)
            
            # Create central widget and layout
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            self.setCentralWidget(central_widget)
            
            # Add text edit for transcription
            self.text_edit = QTextEdit()
            self.text_edit.setFont(QFont("Arial", 12))
            layout.addWidget(self.text_edit)
            
            # Add status label
            self.status_label = QLabel("Status: Ready")
            layout.addWidget(self.status_label)
            
            # Add start button
            self.start_button = QPushButton("Start Dictation")
            self.start_button.clicked.connect(self.toggle_dictation)
            layout.addWidget(self.start_button)
            
            # Add clear button
            self.clear_button = QPushButton("Clear Text")
            self.clear_button.clicked.connect(lambda: self.text_edit.clear())
            layout.addWidget(self.clear_button)
            
            # Set dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QTextEdit {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 2px solid #3c3c3c;
                    padding: 10px;
                }
                QLabel {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #3c3c3c;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            
            logging.info("UI initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing UI: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize UI: {str(e)}")
            sys.exit(1)

    def toggle_dictation(self):
        try:
            if not self.is_listening:
                self.start_button.setText("Stop Dictation")
                self.is_listening = True
                logging.info("Dictation started")
                self.status_label.setText("Status: Recording")
                
            else:
                self.start_button.setText("Start Dictation")
                self.is_listening = False
                self.status_label.setText("Status: Stopped")
                
        except Exception as e:
            logging.error(f"Error in toggle_dictation: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to toggle dictation: {str(e)}")

    def callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def process_audio_loop(self):
        logging.info("Starting audio processing loop")
        stream = None
        
        while True:
            if not self.is_listening:
                time.sleep(0.1)
                continue
            
            try:
                # Only create stream once and keep it open
                if stream is None:
                    stream = self.audio.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk_size,
                        stream_callback=self.callback
                    )
                    logging.info("Audio stream created successfully")
                    
                if not stream.is_active():
                    stream.start_stream()
                    logging.info("Audio stream started")
                    
                while self.is_listening:
                    try:
                        if not self.audio_queue.empty():
                            audio_data = self.audio_queue.get()
                            if audio_data is None:
                                continue
                                
                            # Update current buffer
                            self.current_buffer = np.concatenate((self.current_buffer, audio_data))
                            
                            # If buffer exceeds max size, process oldest chunk
                            if len(self.current_buffer) > self.max_buffer_size:
                                oldest_chunk = self.current_buffer[:self.window_size]
                                self.current_buffer = self.current_buffer[self.window_size:]
                                
                                try:
                                    # Convert to float32 and normalize
                                    audio_float = oldest_chunk.astype(np.float32) / 32768.0
                                    
                                    # Check for silence
                                    rms = np.sqrt(np.mean(audio_float**2))
                                    if rms < self.silence_threshold:
                                        self.silence_counter += 1
                                    else:
                                        self.silence_counter = 0
                                    
                                    # Process if we have enough speech or silence is detected
                                    if self.silence_counter >= self.min_silence_duration * self.sample_rate / self.chunk_size:
                                        try:
                                            logging.info("Starting transcription")
                                            result = self.model.transcribe(
                                                audio_float,
                                                language="en",
                                                fp16=torch.cuda.is_available(),
                                                temperature=0.0,
                                                best_of=1,
                                                verbose=False,
                                                word_timestamps=True
                                            )
                                            
                                            text = result["text"]
                                            segments = result.get("segments", [])
                                            
                                            if segments and text and not text.isspace():
                                                # Get confidence from the last segment
                                                confidence = segments[-1]["no_speech_prob"] if "no_speech_prob" in segments[-1] else 0.0
                                                
                                                if confidence < self.confidence_threshold:
                                                    # Process text with minimal delay
                                                    text = text.strip()
                                                    if text.lower() != self.last_text.lower():
                                                        self.last_text = text
                                                        self.text_edit.insertPlainText(text)
                                                        cursor = self.text_edit.textCursor()
                                                        cursor.movePosition(cursor.MoveOperation.End)
                                                        self.text_edit.setTextCursor(cursor)
                                                        logging.info(f"Transcribed text: {text}")
                                                
                                        except Exception as e:
                                            logging.error(f"Error in transcription: {str(e)}", exc_info=True)
                                            self.current_buffer = np.array([], dtype=np.int16)
                                            continue
                                except Exception as e:
                                    logging.error(f"Error processing audio chunk: {str(e)}", exc_info=True)
                                    self.current_buffer = np.array([], dtype=np.int16)
                                    continue
                    except Exception as e:
                        logging.error(f"Error processing audio data: {str(e)}", exc_info=True)
                        self.current_buffer = np.array([], dtype=np.int16)
                        continue
                    
                    time.sleep(0.001)  # Reduced delay for faster response
                
            except Exception as e:
                logging.error(f"Error in audio stream: {str(e)}", exc_info=True)
                time.sleep(0.1)
                continue
            finally:
                if stream:
                    try:
                        stream.stop_stream()
                        stream.close()
                        stream = None
                        logging.info("Audio stream stopped and closed")
                    except Exception as e:
                        logging.error(f"Error closing stream: {str(e)}", exc_info=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dictation_app = EnglishDictation()
    dictation_app.show()
    sys.exit(app.exec())
