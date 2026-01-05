# Building Monitor.exe

This guide explains how to package the PC Gaming Monitor app as a standalone executable.

## Prerequisites

1. Install all dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have all the required files:
   - `Monitor.py` (main application)
   - `templates/` folder (HTML templates)
   - `static/` folder (CSS and JavaScript)
   - `lib/` folder (DLLs and executables)
   - `utils/` folder (utility modules)
   - `icon.png` (application icon)

## Method 1: Using the Build Script (Recommended)

Simply run:
```bash
build.bat
```

This will:
- Check if PyInstaller is installed
- Install it if needed
- Build the executable using the spec file
- Create `Monitor.exe` in the `dist/` folder

## Method 2: Using PyInstaller Directly

### Option A: Using the spec file
```bash
pyinstaller Monitor.spec
```

### Option B: Using command line
```bash
pyinstaller --name=Monitor --onefile --windowed --icon=icon.png ^
    --add-data="templates;templates" ^
    --add-data="static;static" ^
    --add-data="lib;lib" ^
    --add-data="utils;utils" ^
    --hidden-import=clr --hidden-import=wmi --hidden-import=pynvml ^
    --hidden-import=pycaw --hidden-import=comtypes Monitor.py
```

## Method 3: Using the Python Build Script

```bash
python build_exe.py
```

## Output

After building, you'll find:
- `Monitor.exe` in the `dist/` folder
- `build/` folder (can be deleted after building)

## Notes

- **Console Window**: The spec file is set to `console=False` (no console window). If you want to see console output for debugging, change it to `console=True` in `Monitor.spec`.

- **File Size**: The executable will be large (50-100MB+) because it includes Python and all dependencies.

- **First Run**: The first time you run the exe, it may take a few seconds to extract and start.

- **Antivirus**: Some antivirus software may flag PyInstaller executables. This is a false positive. You may need to add an exception.

- **Dependencies**: Make sure all DLL files in the `lib/` folder are included. The spec file should handle this automatically.

## Troubleshooting

### "Module not found" errors
- Add missing modules to `hiddenimports` in `Monitor.spec`
- Rebuild with `--clean` flag: `pyinstaller --clean Monitor.spec`

### Missing files (templates, static, etc.)
- Check that `datas` in `Monitor.spec` includes all necessary folders
- Verify file paths are correct

### Large file size
- This is normal for PyInstaller one-file executables
- Consider using `--onedir` instead of `--onefile` for smaller size (but multiple files)

### DLL errors
- Make sure `lib/OpenHardwareMonitorLib.dll` is included
- Check that all required DLLs are in the `lib/` folder

## Distribution

To distribute your app:
1. Build the executable using one of the methods above
2. Test the `Monitor.exe` on a clean system (without Python installed)
3. Create a zip file with:
   - `Monitor.exe`
   - Any additional README or license files
4. Share the zip file

The executable is standalone and doesn't require Python to be installed on the target machine.

