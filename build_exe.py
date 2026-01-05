"""
Build script for creating Monitor.exe using PyInstaller
Run: python build_exe.py
"""
import PyInstaller.__main__
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
args = [
    'Monitor.py',
    '--name=Monitor',
    '--onefile',
    '--windowed',  # No console window (use --noconsole if you want console)
    '--icon=icon.png',
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--add-data=lib;lib',
    '--add-data=utils;utils',
    '--hidden-import=clr',
    '--hidden-import=wmi',
    '--hidden-import=pynvml',
    '--hidden-import=pycaw',
    '--hidden-import=comtypes',
    '--hidden-import=OpenHardwareMonitor',
    '--collect-all=pycaw',
    '--collect-all=comtypes',
    '--noconfirm',
    '--clean'
]

# Change to script directory
os.chdir(script_dir)

# Run PyInstaller
PyInstaller.__main__.run(args)

