# Dhivehi Dictation System

A real-time speech-to-text dictation system for the Dhivehi language using Wav2Vec2 and Shakeem models.

## Current Status

### Progress Made
- Basic PyQt5 GUI with dark theme implemented
- Audio input functionality with sounddevice
- Voice activity detection with WebRTC VAD
- Model loading and processing with transformers and torch
- Real-time text display

### Build System Development
- Initial PyInstaller build attempts
- Minimal test applications for dependency testing
- cx_Freeze alternative build system
- Python version compatibility testing

### Dependencies
- Python 3.10
- PyQt5 5.15.9
- cx_Freeze 6.15
- transformers 4.30.2
- torch 2.0.1
- numpy 1.21.6
- sounddevice 0.4.6
- soundfile 0.12.1
- webrtcvad 2.0.10
- scipy 1.7.3

## Build System Status

### Current Issues
- PyInstaller build fails with Python 3.10 bytecode handling
- cx_Freeze build fails with virtual environment activation
- Need to resolve dependency conflicts

### Next Steps
1. Investigate alternative Python versions (3.8/3.9)
2. Simplify build process
3. Test minimal functionality first
4. Add error handling and logging
5. Create proper build documentation

## Development Files

- `main.py`: Main application code
- `setup.py`: Build configuration
- `test_app.py`: Minimal test application
- `test_sounddevice.py`: Audio input test
- `test_transformers.py`: Model loading test
- `build*.ps1`: Build scripts
- `requirements*.txt`: Dependency files

## Notes

- The application is in active development
- Build system issues need resolution
- Documentation will be updated as development progresses

## Model Setup

1. Place your Wav2Vec2 model files in the `model` directory
2. The model directory should contain:
   - config.json
   - pytorch_model.bin
   - tokenizer.json
   - Any other required model files

The application will automatically use the model files from this directory.

## Setup

1. Initial Setup (one-time only):
```bash
setup.bat
```
This will:
- Create a virtual environment
- Install all dependencies
- Set up the model directory
- Create initial shortcuts

2. Build the Application:
```bash
build_all.bat
```
This will:
- Build the standalone executable with all dependencies
- Create proper shortcuts
- Clean up build files
- Verify the executable is created successfully

3. Run the Application:
- Double-click "Dhivehi Dictation.exe" in the main directory
- OR use the desktop shortcut
- OR run "start_dhivehi_dictation.bat"

   - pytorch_model.bin
   - tokenizer.json
   - Any other required model files

The application will automatically use the model files from this directory.

## Build Notes

- The build process now properly handles all dependencies
- The executable is created in the `dist` directory and then moved to the main directory
- Proper error checking is in place for the build process
- The application uses a proper working directory when launched
- All required dependencies are included in the executable

## Troubleshooting

If the build fails:
1. Make sure all dependencies are installed using `setup.bat`
2. Verify you have enough disk space
3. Check that no antivirus is blocking the build process
4. Try running `build_all.bat` as administrator if permissions are an issue

## Usage

1. Launch the application
2. Click "Load Model" and select your model directory
3. Click "Start Dictation" to begin
4. Speak clearly in Dhivehi
5. Click "Stop Dictation" when finished

## Model Training

To train your own model:

1. Prepare your dataset with audio recordings and corresponding text
2. Fine-tune a Wav2Vec2 model using your dataset
3. Save the model and select it using the "Load Model" button in the application

## Requirements

- Python 3.8+
- Microphone
- Internet connection (for initial model download)
- CUDA-compatible GPU (recommended for faster processing)
- Windows operating system
