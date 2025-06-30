import streamlit as st
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile
import os
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import webrtcvad
import queue
import threading

class DhivehiDictation:
    def __init__(self):
        self.processor = None
        self.model = None
        self.audio_queue = queue.Queue()
        self.text_output = ""
        self.is_recording = False
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # Aggressive mode
        
        # Initialize Streamlit interface
        self.setup_ui()

    def setup_ui(self):
        st.set_page_config(
            page_title="Dhivehi Dictation",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Dark theme
        st.markdown("""
        <style>
        .stApp {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .stTextInput {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)

    def start_recording(self):
        self.is_recording = True
        self.audio_queue.queue.clear()
        
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
        # Convert to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
            
        # Convert to 16kHz if needed
        if audio_data.shape[0] > 0:
            # Process audio in chunks
            chunk_size = 16000  # 1 second chunks
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                if len(chunk) > 0:
                    self.transcribe_chunk(chunk)

    def transcribe_chunk(self, audio_chunk):
        if self.processor is None or self.model is None:
            return
            
        # Preprocess audio
        input_values = self.processor(audio_chunk, sampling_rate=16000, return_tensors="pt").input_values
        
        # Get logits from model
        logits = self.model(input_values).logits
        
        # Take argmax and decode
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.decode(predicted_ids[0])
        
        # Update text output
        self.text_output += transcription + " "
        st.text_area("Transcription", value=self.text_output, height=400)

    def run(self):
        st.title("Dhivehi Dictation System")
        
        # Model loading
        model_name = st.text_input("Model Name", "wav2vec2-dhivehi")
        if st.button("Load Model"):
            try:
                self.processor = Wav2Vec2Processor.from_pretrained(model_name)
                self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
                st.success("Model loaded successfully!")
            except Exception as e:
                st.error(f"Error loading model: {str(e)}")

        # Start/Stop recording
        if st.button("Start Dictation"):
            self.start_recording()
        
        if st.button("Stop Dictation"):
            self.is_recording = False

if __name__ == "__main__":
    app = DhivehiDictation()
    app.run()
