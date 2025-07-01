import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from threading import Thread
import time
import sounddevice as sd
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2FeatureExtractor
import torch
import numpy as np
from queue import Queue
import logging
import os
from docx import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model and processor
try:
    logger.info("Loading model and processor...")
    processor = Wav2Vec2Processor.from_pretrained("./model", local_files_only=True)
    processor.sampling_rate = 16000  # Set sampling rate explicitly
    model = Wav2Vec2ForCTC.from_pretrained("./model", local_files_only=True)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise RuntimeError("Failed to load model. Please check if the model directory exists and contains all required files.")

# Initialize audio queue
q = Queue()

def audio_callback(indata, frames, time, status):
    if status:
        logger.warning(f"Audio status: {status}")
    q.put(indata.copy())

def transcribe(audio_chunk):
    try:
        # Convert audio to appropriate format
        audio_chunk = np.squeeze(audio_chunk)
        if len(audio_chunk.shape) > 1:
            audio_chunk = audio_chunk.mean(axis=1)
        
        # Process audio in chunks
        chunk_size = 16000  # 1 second chunks
        chunks = [audio_chunk[i:i+chunk_size] for i in range(0, len(audio_chunk), chunk_size)]
        
        # Process chunks in reverse order for RTL text
        full_text = ""
        for chunk in reversed(chunks):
            if len(chunk) < 1000:  # Skip very short chunks
                continue
                
            # Process chunk
            input_values = processor(chunk, return_tensors="pt").input_values
            logits = model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            text = processor.decode(predicted_ids[0])
            
            # Filter out empty or very short transcriptions
            if text and len(text.strip()) > 2:
                # Split into words and reverse for RTL
                words = text.strip().split()
                words.reverse()
                full_text += " ".join(words) + " "
                
        return full_text.strip()
        
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}")
        return ""

def save_document(text_area):
    try:
        content = text_area.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showwarning("Empty Document", "The document is empty!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx"), ("All Files", "*.*")]
        )
        
        if filename:
            doc = Document()
            doc.add_paragraph(content)
            doc.save(filename)
            messagebox.showinfo("Success", f"Document saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving document: {str(e)}")

def new_document(text_area):
    if messagebox.askyesno("New Document", "Are you sure you want to create a new document? This will clear the current content."):
        text_area.delete("1.0", "end")

def start_gui():
    root = tk.Tk()
    root.title("Dhisaaj - Dhivehi Dictation Tool")
    root.geometry("1000x700")
    
    # Modern color scheme
    bg_color = "#1e1e1e"
    fg_color = "#ffffff"
    button_bg = "#3c3f41"
    button_fg = "#ffffff"
    text_bg = "#2b2b2b"
    text_fg = "#ffffff"
    accent_color = "#0078d7"
    
    # Create main frame with padding
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title frame
    title_frame = tk.Frame(main_frame, bg=bg_color)
    title_frame.pack(fill="x", pady=(0, 20))
    
    title_label = tk.Label(title_frame, text="Dhisaaj - Dhivehi Dictation", 
                          font=("Arial", 24, "bold"), bg=bg_color, fg=accent_color)
    title_label.pack(side="left")
    
    # Create control panel
    control_panel = tk.Frame(main_frame, bg=bg_color)
    control_panel.pack(fill="x", pady=(0, 20))
    
    # Create buttons with modern styling
    def create_button(text, command, width=10):
        return tk.Button(control_panel, text=text, command=command,
                        bg=button_bg, fg=button_fg,
                        activebackground=accent_color,
                        activeforeground=fg_color,
                        padx=15, pady=8, width=width,
                        font=("Arial", 10))
    
    # Save button
    save_button = create_button("Save", lambda: save_document(text_area))
    save_button.pack(side="left", padx=5)
    
    # New button
    new_button = create_button("New", lambda: new_document(text_area))
    new_button.pack(side="left", padx=5)
    
    # Dictation control
    dictation_var = tk.StringVar(value="Start")
    dictation_button = create_button("Start", lambda: toggle_dictation(dictation_var))
    dictation_button.pack(side="left", padx=5)
    
    # Text direction toggle
    direction_var = tk.StringVar(value="RTL")
    direction_frame = tk.Frame(control_panel, bg=bg_color)
    direction_frame.pack(side="left", padx=20)
    
    tk.Label(direction_frame, text="Text Direction:", bg=bg_color, fg=fg_color,
             font=("Arial", 10)).pack(side="left")
    
    def toggle_direction():
        current = direction_var.get()
        new = "RTL" if current == "LTR" else "LTR"
        direction_var.set(new)
        
        # Remove existing tags
        text_area.tag_remove("rtl", "1.0", "end")
        text_area.tag_remove("ltr", "1.0", "end")
        
        # Add new tag
        text_area.tag_add(direction_var.get().lower(), "1.0", "end")
        
        # Configure tags
        text_area.tag_configure("rtl", justify="right", background=text_bg, foreground=text_fg)
        text_area.tag_configure("ltr", justify="left", background=text_bg, foreground=text_fg)
        
        # Update cursor position
        update_cursor_position()
    
    direction_button = create_button(direction_var.get(), toggle_direction, width=5)
    direction_button.pack(side="left")
    
    # Cursor position label
    cursor_label = tk.Label(control_panel, text="Cursor: 0:0", bg=bg_color, fg=fg_color,
                           font=("Arial", 10))
    cursor_label.pack(side="right", padx=10)
    
    # Create text area with improved styling
    text_frame = tk.Frame(main_frame, bg=bg_color)
    text_frame.pack(fill="both", expand=True)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    
    text_area = tk.Text(text_frame, wrap="word", font=("Faruma", 16), 
                        bg=text_bg, fg=text_fg, yscrollcommand=scrollbar.set,
                        insertbackground="white", spacing1=5, spacing2=2, spacing3=5)
    text_area.pack(fill="both", expand=True)
    scrollbar.config(command=text_area.yview)
    
    # Configure text direction
    text_area.tag_configure("rtl", justify="right", background=text_bg, foreground=text_fg)
    text_area.tag_configure("ltr", justify="left", background=text_bg, foreground=text_fg)
    text_area.tag_add(direction_var.get().lower(), "1.0", "end")
    
    # Add cursor position tracking
    def update_cursor_position(event=None):
        row, col = text_area.index("insert").split('.')
        cursor_label.config(text=f"Cursor: {row}:{col}")
    
    text_area.bind('<KeyRelease>', update_cursor_position)
    text_area.bind('<ButtonRelease>', update_cursor_position)
    
    # Dictation control variables
    dictation_thread = None
    dictation_running = False
    dictation_queue = []  # Queue for ordered dictation
    current_index = 0  # Track current position in queue
    
    def toggle_dictation(button_var):
        nonlocal dictation_thread, dictation_running, dictation_queue, current_index
        
        if not dictation_running:
            # Start dictation
            dictation_running = True
            button_var.set("Stop")
            dictation_queue = []
            current_index = 0
            dictation_thread = Thread(target=dictation_thread_func, daemon=True)
            dictation_thread.start()
        else:
            # Stop dictation
            dictation_running = False
            button_var.set("Start")
            try:
                dictation_thread.join(timeout=1)
            except:
                pass
    
    def insert_text(text):
        nonlocal current_index
        
        # Get current cursor position
        cursor_pos = text_area.index("insert")
        
        # Add text to queue with position
        dictation_queue.append((cursor_pos, text))
        dictation_queue.sort(key=lambda x: x[0])  # Sort by position
        
        # Find our position in queue
        for i, (pos, _) in enumerate(dictation_queue):
            if pos == cursor_pos:
                current_index = i
                break
        
        # Insert text at current position
        text_area.insert(cursor_pos, text + " ")
        
        # Update cursor position
        update_cursor_position()
    
    def dictation_thread_func():
        while dictation_running:
            try:
                # Get audio chunk with timeout
                audio_chunk = q.get(timeout=5)
                if audio_chunk is None:
                    continue
                    
                # Process audio chunk
                text = transcribe(audio_chunk)
                if text:
                    insert_text(text)
            except Queue.Empty:
                continue
            except Exception as e:
                print(f"Error in dictation: {str(e)}")
                continue
            
            # Small delay to prevent CPU overload
            time.sleep(0.1)
    
    # Add status bar at bottom
    status_bar = tk.Label(main_frame, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                         bg=bg_color, fg=fg_color, font=("Arial", 10))
    status_bar.pack(side="bottom", fill="x", pady=(10, 0))
    
    def update_status(text):
        status_bar.config(text=f"Status: {text}")
    
    # Bind status updates
    dictation_button.config(command=lambda: toggle_dictation(dictation_var))
    dictation_button.bind('<Button-1>', lambda e: update_status("Dictation Running" if dictation_var.get() == "Stop" else "Ready"))
    
    root.mainloop()

if __name__ == "__main__":
    try:
        # Check Python version
        import sys
        if sys.version_info < (3, 6):
            raise RuntimeError("Python 3.6 or higher is required")
            
        # Check required packages
        required_packages = [
            'sounddevice',
            'torch',
            'transformers',
            'numpy',
            'python-docx'
        ]
        
        import importlib
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            raise RuntimeError(f"Missing required packages: {', '.join(missing_packages)}")
            
        # Check if model directory exists
        if not os.path.exists("./model"):
            raise RuntimeError("Model directory not found! Please download and install the model first.")
            
        # Check if required model files exist
        required_files = [
            "config.json",
            "pytorch_model.bin",
            "preprocessor_config.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join("model", file)):
                missing_files.append(file)
        
        if missing_files:
            raise RuntimeError(f"Missing model files: {', '.join(missing_files)}")
            
        # Start the GUI
        start_gui()
        
    except RuntimeError as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Error", str(e))
        root.quit()
        
    except Exception as e:
        import traceback
        print(f"Unexpected error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        root.quit()
