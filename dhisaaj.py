import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from threading import Thread
from typing import Optional # Added for type hinting
import time
import sounddevice as sd
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import numpy as np
from queue import Queue
import logging
import os
import sys # Added for sys.exit and sys.stdout
from docx import Document

# --- Global Variables ---
# These will be initialized in the main block after checks.
processor: Optional[Wav2Vec2Processor] = None
model: Optional[Wav2Vec2ForCTC] = None
logger: Optional[logging.Logger] = None # Will be initialized by main

# Initialize audio queue
q = Queue()
# Global reference to the audio stream object
audio_stream = None


# --- Constants ---
MODEL_SAMPLING_RATE = 16000  # Hz
AUDIO_CHANNELS = 1           # Mono audio
# MODEL_PROCESS_CHUNK_SIZE_SECONDS = 1 # This was an idea, but processor handles chunking.
MODEL_PROCESS_CHUNK_SIZE_SAMPLES = 16000 # Process this many samples at a time by the model (e.g., 1 second)
MIN_AUDIO_CHUNK_SAMPLES_FOR_TRANSCRIPTION = 1000 # Min samples for a chunk to be transcribed (e.g., ~60ms)


# --- Audio Handling ---

def audio_callback(indata: np.ndarray, frames: int, time_info, status: sd.CallbackFlags) -> None:
    """
    This callback is invoked by sounddevice from a separate thread for each block of incoming audio data.
    """
    global logger # Ensure logger is accessible
    if status:
        if logger: logger.warning(f"Audio Callback Status: {status}")
        else: print(f"Audio Callback Status (logger not init): {status}")
    q.put(indata.copy())

def transcribe(audio_chunk: np.ndarray) -> str:
    """
    Transcribes a given audio chunk using the pre-loaded Wav2Vec2 model.
    The audio_chunk is expected to be a numpy array of raw audio samples.
    """
    global processor, model, logger # Ensure access to global model/processor and logger
    if not processor or not model:
        if logger: logger.error("Transcription called but model or processor not loaded.")
        else: print("Transcription called but model or processor not loaded.")
        return ""

    try:
        audio_chunk = np.squeeze(audio_chunk)
        if len(audio_chunk.shape) > 1:
            audio_chunk = audio_chunk.mean(axis=1)
        
        model_input_chunks = [
            audio_chunk[i:i + MODEL_PROCESS_CHUNK_SIZE_SAMPLES]
            for i in range(0, len(audio_chunk), MODEL_PROCESS_CHUNK_SIZE_SAMPLES)
        ]
        
        full_text_parts = []
        for chunk_segment in model_input_chunks:
            if len(chunk_segment) < MIN_AUDIO_CHUNK_SAMPLES_FOR_TRANSCRIPTION:
                if logger: logger.debug(f"Skipping very short audio chunk segment: {len(chunk_segment)} samples")
                continue

            input_values = processor(chunk_segment, return_tensors="pt", sampling_rate=MODEL_SAMPLING_RATE).input_values
            logits = model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            text_segment = processor.decode(predicted_ids[0])
            
            if text_segment and len(text_segment.strip()) > 0:
                full_text_parts.append(text_segment.strip())
                
        return " ".join(full_text_parts)
        
    except Exception as e:
        if logger: logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        else: print(f"Error during transcription (logger not init): {str(e)}")
        return ""


# --- GUI Related Functions ---

def save_document(text_area: tk.Text) -> None:
    global logger
    try:
        content = text_area.get("1.0", tk.END + "-1c") # Correct way to get all text except trailing newline
        if not content.strip():
            messagebox.showwarning("Empty Document", "The document is empty. Nothing to save.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx"), ("Text Document", "*.txt"), ("All Files", "*.*")]
        )
        
        if filename:
            if filename.endswith(".docx"):
                doc = Document()
                doc.add_paragraph(content)
                doc.save(filename)
            else: # Save as plain text
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            messagebox.showinfo("Success", f"Document saved successfully to {filename}")
            if logger: logger.info(f"Document saved to {filename}")
    except Exception as e:
        if logger: logger.error(f"Error saving document: {str(e)}", exc_info=True)
        messagebox.showerror("Save Error", f"An error occurred while saving the document: {str(e)}")

def new_document(text_area: tk.Text) -> None:
    global logger
    try:
        if text_area.get("1.0", tk.END + "-1c").strip(): # Check if there's content
            if messagebox.askyesno("New Document",
                                   "Are you sure you want to create a new document?\n"
                                   "All unsaved changes in the current document will be lost."):
                text_area.delete("1.0", tk.END)
                if logger: logger.info("New document created, text area cleared.")
        else: # If no content, just clear (though it should be empty)
            text_area.delete("1.0", tk.END)
            if logger: logger.info("Text area already empty or cleared for new document.")
    except Exception as e:
        if logger: logger.error(f"Error creating new document: {str(e)}", exc_info=True)
        messagebox.showerror("New Document Error", f"An error occurred: {str(e)}")

# --- Main GUI Setup ---
def start_gui() -> None:
    global logger # Ensure logger is accessible
    root = tk.Tk()
    root.title("Dhisaaj - Dhivehi Dictation Tool")
    root.geometry("1000x700")
    
    bg_color = "#1e1e1e"
    fg_color = "#ffffff"
    button_bg = "#3c3f41"
    text_bg = "#2b2b2b"
    accent_color = "#0078d7"
    
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title_frame = tk.Frame(main_frame, bg=bg_color)
    title_frame.pack(fill=tk.X, pady=(0, 20))
    
    title_label = tk.Label(title_frame, text="Dhisaaj - Dhivehi Dictation", 
                          font=("Arial", 24, "bold"), bg=bg_color, fg=accent_color)
    title_label.pack(side=tk.LEFT)
    
    control_panel = tk.Frame(main_frame, bg=bg_color)
    control_panel.pack(fill=tk.X, pady=(0, 20))

    def create_styled_button(parent: tk.Widget, text: str, command: callable, width: int = 10) -> tk.Button:
        return tk.Button(parent, text=text, command=command,
                         bg=button_bg, fg=fg_color,
                         activebackground=accent_color, activeforeground=fg_color,
                         padx=15, pady=8, width=width,
                         font=("Arial", 10), relief=tk.FLAT, borderwidth=0)

    text_area = tk.Text(main_frame, wrap=tk.WORD, font=("Faruma", 16),
                        bg=text_bg, fg=fg_color, insertbackground=fg_color,
                        spacing1=5, spacing2=2, spacing3=5, relief=tk.FLAT, borderwidth=0)
    
    save_button = create_styled_button(control_panel, "Save", lambda: save_document(text_area))
    save_button.pack(side=tk.LEFT, padx=5)
    
    new_button = create_styled_button(control_panel, "New", lambda: new_document(text_area))
    new_button.pack(side=tk.LEFT, padx=5)
    
    dictation_var = tk.StringVar(value="Start")
    
    status_bar = tk.Label(main_frame, text="Status: Initializing...", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                    bg=bg_color, fg=fg_color, font=("Arial", 10))

    def update_status(text: str) -> None:
        if status_bar.winfo_exists():
            status_bar.config(text=f"Status: {text}")
        if logger: logger.info(f"Status updated: {text}")
        else: print(f"Status updated (logger not init): {text}")

    dictation_button = create_styled_button(control_panel, dictation_var.get(),
                                           lambda: toggle_dictation(dictation_var)) # Corrected: update_status removed from here
    dictation_button.pack(side=tk.LEFT, padx=5)
    dictation_var.trace_add("write", lambda *args: dictation_button.config(text=dictation_var.get()))

    direction_var = tk.StringVar(value="RTL")
    direction_frame = tk.Frame(control_panel, bg=bg_color)
    direction_frame.pack(side=tk.LEFT, padx=20)
    
    tk.Label(direction_frame, text="Text Direction:", bg=bg_color, fg=fg_color,
             font=("Arial", 10)).pack(side=tk.LEFT)
    
    def toggle_text_direction() -> None:
        current_direction = direction_var.get()
        new_direction = "LTR" if current_direction == "RTL" else "RTL"
        direction_var.set(new_direction)
        direction_toggle_button.config(text=new_direction)
        text_area.tag_remove("rtl_align", "1.0", tk.END)
        text_area.tag_remove("ltr_align", "1.0", tk.END)
        if new_direction == "RTL": text_area.tag_add("rtl_align", "1.0", tk.END)
        else: text_area.tag_add("ltr_align", "1.0", tk.END)
    
    direction_toggle_button = create_styled_button(direction_frame, direction_var.get(),
                                                 toggle_text_direction, width=5)
    direction_toggle_button.pack(side=tk.LEFT)
    
    cursor_label = tk.Label(control_panel, text="Cursor: 1.0", bg=bg_color, fg=fg_color, font=("Arial", 10))
    cursor_label.pack(side=tk.RIGHT, padx=10)
    
    text_frame_outer = tk.Frame(main_frame, bg=bg_color) # For padding around text_area and scrollbar
    text_frame_outer.pack(fill=tk.BOTH, expand=True, pady=(0,5)) # Padding at bottom before status bar
    
    scrollbar = tk.Scrollbar(text_frame_outer, relief=tk.FLAT, troughcolor=text_bg) # Adjusted troughcolor
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_area.pack(in_=text_frame_outer, side=tk.LEFT, fill=tk.BOTH, expand=True) # Pack text_area inside text_frame_outer
    scrollbar.config(command=text_area.yview)
    text_area.config(yscrollcommand=scrollbar.set) # Ensure this is set
    
    text_area.tag_configure("rtl_align", justify=tk.RIGHT)
    text_area.tag_configure("ltr_align", justify=tk.LEFT)
    text_area.tag_add("rtl_align", "1.0", tk.END)
    
    def update_cursor_position(event=None) -> None:
        if text_area.winfo_exists():
            row, col = text_area.index(tk.INSERT).split('.')
            cursor_label.config(text=f"Cursor: {int(row)}:{col}")
    
    text_area.bind('<KeyRelease>', update_cursor_position)
    text_area.bind('<ButtonRelease>', update_cursor_position)
    update_cursor_position()
    
    dictation_thread: Optional[Thread] = None
    dictation_running: bool = False
    audio_stream_active: bool = False
    app_root: tk.Tk = root

    status_bar.pack(side=tk.BOTTOM, fill=tk.X) # pady removed, handled by text_frame_outer
    update_status("Ready")

    def start_audio_stream_gui_cb() -> None:
        nonlocal audio_stream, audio_stream_active, dictation_running, dictation_var
        if audio_stream_active: return
        try:
            while not q.empty():
                try: q.get_nowait()
                except Queue.Empty: break
            audio_stream = sd.InputStream(samplerate=MODEL_SAMPLING_RATE, channels=AUDIO_CHANNELS,
                                          callback=audio_callback, dtype='float32')
            audio_stream.start()
            audio_stream_active = True
            if logger: logger.info("Audio stream started.")
            update_status("Listening...")
        except Exception as e:
            if logger: logger.error(f"Fatal error starting audio stream: {e}", exc_info=True)
            messagebox.showerror("Audio Error", f"Could not start audio input: {e}")
            dictation_running = False
            if dictation_var.get() == "Stop": dictation_var.set("Start")
            audio_stream_active = False
            update_status("Error: Audio stream failed.")

    def stop_audio_stream_gui_cb() -> None:
        nonlocal audio_stream, audio_stream_active
        if not audio_stream_active or not audio_stream:
            if audio_stream_active and not audio_stream:
                 if logger: logger.warning("stop_audio_stream_gui_cb: audio_stream_active is True but audio_stream is None.")
            audio_stream_active = False
            return
        try:
            if logger: logger.info("Attempting to stop audio stream...")
            audio_stream.stop(); audio_stream.close()
            if logger: logger.info("Audio stream stopped/closed.")
        except Exception as e:
            if logger: logger.error(f"Error stopping audio stream: {e}", exc_info=True)
        finally:
            audio_stream = None; audio_stream_active = False
            if not dictation_running: update_status("Ready")

    def toggle_dictation(button_tk_var: tk.StringVar) -> None:
        nonlocal dictation_thread, dictation_running, audio_stream_active
        if not dictation_running:
            update_status("Starting dictation...")
            dictation_running = True
            button_tk_var.set("Stop")
            start_audio_stream_gui_cb()
            if audio_stream_active:
                if logger: logger.info("Audio stream active, starting dictation thread.")
                dictation_thread = Thread(target=dictation_thread_func,
                                          args=(app_root, text_area, update_cursor_position, update_status),
                                          daemon=True)
                dictation_thread.start()
            else:
                if logger: logger.warning("Dictation start aborted: audio stream not active.")
                dictation_running = False; button_tk_var.set("Start")
        else:
            update_status("Stopping dictation...")
            dictation_running = False
            button_tk_var.set("Start")
            stop_audio_stream_gui_cb()
            if dictation_thread and dictation_thread.is_alive():
                if logger: logger.info("Waiting for dictation thread...")
                try:
                    dictation_thread.join(timeout=1.5)
                    if dictation_thread.is_alive():
                        if logger: logger.warning("Dictation thread join timeout.")
                except Exception as e:
                    if logger: logger.error(f"Error joining dictation thread: {e}", exc_info=True)
            if logger: logger.info("Dictation process stopped.")

    def on_app_closing() -> None:
        nonlocal dictation_running, dictation_thread
        if logger: logger.info("Application closing...")
        if dictation_running:
            dictation_running = False
            if dictation_thread and dictation_thread.is_alive():
                dictation_thread.join(timeout=0.75)
        stop_audio_stream_gui_cb()
        if app_root.winfo_exists(): app_root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_app_closing)

    def schedule_text_insertion(target_text_area: tk.Text, text_to_insert: str, cursor_update_cb: callable) -> None:
        if target_text_area.winfo_exists():
            target_text_area.insert(tk.INSERT, text_to_insert + " ")
            cursor_update_cb()

    def dictation_thread_func(ui_root: tk.Tk, target_text_area: tk.Text,
                              cursor_update_cb: callable, status_updater_cb: callable) -> None:
        nonlocal dictation_running
        is_processing: bool = False
        if logger: logger.info("Dictation thread started.")
        while dictation_running:
            try:
                audio_chunk_data = q.get(timeout=0.2)
                if not is_processing:
                    ui_root.after(0, lambda: status_updater_cb("Processing..."))
                    is_processing = True
                transcribed_text = transcribe(audio_chunk_data)
                if transcribed_text:
                    ui_root.after(0, lambda text=transcribed_text: schedule_text_insertion(target_text_area, text, cursor_update_cb))
                if dictation_running and is_processing:
                    ui_root.after(0, lambda: status_updater_cb("Listening..."))
                    is_processing = False
            except Queue.Empty:
                if dictation_running and is_processing:
                    ui_root.after(0, lambda: status_updater_cb("Listening..."))
                    is_processing = False
                continue
            except Exception as e:
                if logger: logger.error(f"Error in dictation thread: {str(e)}", exc_info=True)
                ui_root.after(0, lambda: status_updater_cb(f"Error. Check logs."))
                is_processing = False; time.sleep(0.1)
                continue
        if logger: logger.info("Dictation thread finished.")
        if not audio_stream_active: ui_root.after(0, lambda: status_updater_cb("Ready"))
    
    if logger: logger.info("Starting Tkinter main loop.")
    root.mainloop()
    if logger: logger.info("Tkinter main loop finished.")

def _display_startup_error_and_exit(error_message: str, is_unexpected: bool = False):
    """Helper to display error via Tkinter messagebox and then exit."""
    global logger
    if logger:
        if is_unexpected: logger.critical(error_message, exc_info=True)
        else: logger.critical(error_message)

    try:
        import tkinter as tk_err
        from tkinter import messagebox as mb_err
        err_root = tk_err.Tk()
        err_root.withdraw()
        title = "Fatal Error" if is_unexpected else "Application Startup Error"
        mb_err.showerror(title, error_message)
        err_root.quit()
    except Exception as e_tk:
        if logger: logger.error(f"Failed to display Tkinter error popup: {e_tk}", exc_info=True)
        print(f"CRITICAL ERROR (Tkinter popup failed):\n{error_message}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__) # Initialize module-level logger

    try:
        logger.info("Application starting up...")
        logger.info("Performing pre-flight system checks...")

        if sys.version_info < (3, 7):
            _display_startup_error_and_exit("Python 3.7 or higher is required.")
        logger.info(f"Python version check passed ({sys.version.split()[0]}).")

        required_pkgs = ['sounddevice', 'torch', 'transformers', 'numpy', 'python-docx']
        logger.info(f"Checking required packages: {required_pkgs}")
        import importlib
        missing_pkgs = [pkg for pkg in required_pkgs if not importlib.util.find_spec(pkg)]
        if missing_pkgs:
            _display_startup_error_and_exit(f"Missing required packages: {', '.join(missing_pkgs)}. Please install them.")
        logger.info("All required packages found.")
            
        model_dir_path = "./model"
        logger.info(f"Checking model directory: '{model_dir_path}'...")
        if not os.path.exists(model_dir_path) or not os.path.isdir(model_dir_path):
            _display_startup_error_and_exit(f"Model directory '{model_dir_path}' not found or is not a directory.")
        logger.info(f"Model directory '{model_dir_path}' found.")
            
        model_files = ["config.json", "pytorch_model.bin", "preprocessor_config.json"]
        logger.info(f"Checking model files in '{model_dir_path}': {model_files}")
        missing_model_fs = [mf for mf in model_files if not os.path.exists(os.path.join(model_dir_path, mf))]
        if missing_model_fs:
            _display_startup_error_and_exit(f"Missing model files in '{model_dir_path}': {', '.join(missing_model_fs)}.")
        logger.info("All required model files found.")
            
        logger.info("Loading Wav2Vec2 model and processor...")
        try:
            processor = Wav2Vec2Processor.from_pretrained(model_dir_path, local_files_only=True)
            if hasattr(processor, 'feature_extractor'): # Ensure sampling rate consistency
                 processor.feature_extractor.sampling_rate = MODEL_SAMPLING_RATE
            else: # Fallback for older transformers or different processor structure
                processor.sampling_rate = MODEL_SAMPLING_RATE

            model = Wav2Vec2ForCTC.from_pretrained(model_dir_path, local_files_only=True)
            logger.info("Model and processor loaded successfully.")
        except Exception as e_model:
            _display_startup_error_and_exit(f"Failed to load model/processor from '{model_dir_path}'. Error: {e_model}", is_unexpected=True)

        logger.info("Pre-flight checks and model loading complete. Starting GUI...")
        start_gui()
        logger.info("Application finished gracefully.")
        
    except SystemExit: # Allow sys.exit to propagate for clean termination
        pass
    except Exception as e_fatal: # Catch-all for any truly unexpected fatal errors
        _display_startup_error_and_exit(f"An unexpected fatal error occurred: {e_fatal}", is_unexpected=True)
