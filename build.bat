@echo off
echo Building Monitor.exe...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please make sure Python is installed and in your PATH.
    pause
    exit /b 1
)

REM Check if Monitor.exe is running and prompt to close it
tasklist /FI "IMAGENAME eq Monitor.exe" 2>NUL | find /I /N "Monitor.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo WARNING: Monitor.exe is currently running!
    echo Please close Monitor.exe before building.
    echo.
    choice /C YN /M "Do you want to close Monitor.exe now"
    if errorlevel 2 (
        echo Build cancelled. Please close Monitor.exe manually and try again.
        pause
        exit /b 1
    )
    if errorlevel 1 (
        echo Closing Monitor.exe...
        taskkill /F /IM Monitor.exe >nul 2>&1
        
        REM Wait and check multiple times to ensure it's closed
        echo Waiting for Monitor.exe to fully close...
        :wait_loop
        timeout /t 1 /nobreak >nul
        tasklist /FI "IMAGENAME eq Monitor.exe" 2>NUL | find /I /N "Monitor.exe">NUL
        if "%ERRORLEVEL%"=="0" (
            echo Still closing... waiting...
            goto wait_loop
        )
        echo Monitor.exe closed successfully.
        timeout /t 2 /nobreak >nul
    )
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

REM Check if Pillow is installed (needed for icon conversion)
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Pillow not found. Installing for icon support...
    python -m pip install Pillow
)

REM Check if PyQt5 is installed (needed for standalone window)
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo PyQt5 not found. Installing for standalone window support...
    python -m pip install PyQt5 PyQtWebEngine
    if errorlevel 1 (
        echo Warning: Failed to install PyQt5. The app will fall back to browser mode.
    )
)

echo.
echo Starting build process...
echo.

REM Try to remove old exe if it exists and is not locked
if exist "dist\Monitor.exe" (
    echo Removing old Monitor.exe...
    del /F /Q "dist\Monitor.exe" >nul 2>&1
    if errorlevel 1 (
        echo Warning: Could not remove old Monitor.exe. It may be locked.
        echo Trying to unlock and remove...
        timeout /t 3 /nobreak >nul
        del /F /Q "dist\Monitor.exe" >nul 2>&1
        if errorlevel 1 (
            echo ERROR: Cannot remove old Monitor.exe. Please:
            echo 1. Close Monitor.exe if it's running
            echo 2. Close any file explorer windows showing the dist folder
            echo 3. Check if antivirus is locking the file
            echo 4. Try running this script as administrator
            pause
            exit /b 1
        )
    )
    echo Old Monitor.exe removed.
    timeout /t 1 /nobreak >nul
)

REM Build using spec file
python -m PyInstaller Monitor.spec

if errorlevel 1 (
    echo.
    echo Build failed!
    echo.
    echo Common issues:
    echo - Monitor.exe may be running - close it and try again
    echo - Antivirus may be blocking the build
    echo - File may be locked by another process
    echo - Try running this script as administrator
    echo - Check the error message above for details
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable is in: dist\Monitor.exe
echo.
pause
