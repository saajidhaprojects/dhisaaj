# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# Get the current directory
base_dir = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), 'main.py')))

block_cipher = None

# Add necessary paths
pathex = [base_dir]

# Add required binaries and data files
binaries = []
datas = collect_data_files('transformers') + collect_data_files('torch') + collect_data_files('scipy')

# Add required binaries and data files
binaries.extend([
    (os.path.join(base_dir, 'sounddevice/_sounddevice_data/portaudio-binaries'), 'sounddevice/_sounddevice_data/portaudio-binaries'),
])

# Add hidden imports
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtWidgets',
    'PyQt5.QtGui',
    'sounddevice._sounddevice_data',
    'transformers',
    'torch',
    'numpy',
    'scipy',
    'torch.nn.functional',
    'torch.distributed',
    'torch.backends.cudnn',
    'torch.utils.cpp_extension',
    'torch.utils.data',
    'torch.utils.hooks',
    'torch.utils.tensorboard',
    'torchvision',
    'transformers.tokenization_utils',
    'transformers.tokenization_utils_base',
    'transformers.tokenization_utils_fast',
    'transformers.file_utils',
    'transformers.modeling_utils',
    'transformers.configuration_utils',
    'transformers.models.wav2vec2',
    'transformers.models.wav2vec2.tokenization_wav2vec2',
    'transformers.models.wav2vec2.modeling_wav2vec2',
    'transformers.models.wav2vec2.processing_wav2vec2',
    'transformers.models.wav2vec2.feature_extraction_wav2vec2',
]

# Create Analysis object
a = Analysis(
    ['main.py'],
    pathex=pathex,
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Dhivehi Dictation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
