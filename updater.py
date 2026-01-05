import os
import subprocess
import sys
import requests
import re

# Import version from config
try:
    from config import APP_VERSION
except ImportError:
    # Fallback if config not available
    APP_VERSION = "2.0.0"

def compare_versions(current, latest):
    """
    Compare two version strings.
    Returns True if latest > current, False otherwise.
    Handles semantic versioning (e.g., 2.0.0, 2.0.1, 2.1.0)
    """
    def version_tuple(version):
        # Remove 'v' prefix and split by dots
        version = version.lstrip('v').strip()
        parts = re.findall(r'\d+', version)
        # Pad with zeros to ensure same length
        return tuple(int(x) for x in parts)
    
    try:
        current_parts = version_tuple(current)
        latest_parts = version_tuple(latest)
        
        # Pad to same length
        max_len = max(len(current_parts), len(latest_parts))
        current_parts = current_parts + (0,) * (max_len - len(current_parts))
        latest_parts = latest_parts + (0,) * (max_len - len(latest_parts))
        
        return latest_parts > current_parts
    except Exception:
        # Fallback to string comparison
        return latest != current

def get_latest_tag_name():
    """
    Fetches the latest release tag from GitHub.
    """
    try:
        url = "https://api.github.com/repos/Samer-Ismael/PC-Gaming-App/releases/latest"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            release_data = response.json()
            tag_name = release_data.get("tag_name", None)
            
            if tag_name:
                # Remove 'v' prefix if present
                return tag_name.lstrip('v').strip()
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching latest version: {e}")
        return None
           
def get_download_url():
    """Get the download URL for the latest release."""
    try:
        url = "https://api.github.com/repos/Samer-Ismael/PC-Gaming-App/releases/latest"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            release_data = response.json()
            
            if release_data.get('assets'):
                # Look for Monitor.exe first
                for asset in release_data['assets']:
                    if asset['name'] == 'Monitor.exe' or asset['name'].endswith('Monitor.exe'):
                        return asset['browser_download_url']
                
                # If no Monitor.exe found, look for any .exe file
                for asset in release_data['assets']:
                    if asset['name'].endswith('.exe'):
                        return asset['browser_download_url']
                
                # If still no exe, return first asset
                return release_data['assets'][0]['browser_download_url']
        return None
    except Exception as e:
        print(f"Error fetching download URL: {e}")
        return None

def check_update():
    """Check if an update is available."""
    try:
        latest_version = get_latest_tag_name()
        if not latest_version:
            return False
        
        # Compare versions using semantic versioning
        current = APP_VERSION.lstrip('v').strip()
        latest = latest_version.lstrip('v').strip()
        
        # Only return True if latest is actually newer
        return compare_versions(current, latest)
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False

def update_app():
    """
    Generate a PowerShell script to update the app and execute it.
    Works for both script and exe modes.
    """
    latest_version = get_latest_tag_name()  
    exe_url = get_download_url() 
    
    if not exe_url:
        print("Failed to retrieve the download URL. Aborting update.")
        return False
    
    # Determine the current executable path
    if sys.frozen:
        # Running as exe
        current_exe_path = sys.executable
        exe_dir = os.path.dirname(current_exe_path)
    else:
        # Running as script
        current_exe_path = os.path.join(os.getcwd(), "Monitor.exe")
        exe_dir = os.getcwd()
    
    # If Monitor.exe doesn't exist in script mode, use the script path
    if not os.path.exists(current_exe_path) and not sys.frozen:
        current_exe_path = sys.executable
        exe_dir = os.path.dirname(current_exe_path)
    
    update_script_path = os.path.join(exe_dir, "update_script.ps1")
    temp_exe_path = os.path.join(exe_dir, "Monitor_new.exe")
    
    powershell_script_content = f"""
# Update script for PC Gaming Monitor
$ErrorActionPreference = "Stop"

try {{
    Write-Host "Downloading new version (v{latest_version})..."
    
    # Download the new version to a temporary file
    Invoke-WebRequest -Uri "{exe_url}" -OutFile "{temp_exe_path}" -UseBasicParsing
    
    Write-Host "Replacing old version..."
    
    # Wait a moment for the current process to close
    Start-Sleep -Seconds 2
    
    # Remove the old app (if it exists)
    if (Test-Path "{current_exe_path}") {{
        Remove-Item -Path "{current_exe_path}" -Force -ErrorAction SilentlyContinue
    }}
    
    # Rename new file to Monitor.exe
    Rename-Item -Path "{temp_exe_path}" -NewName "Monitor.exe" -Force
    
    Write-Host "Launching new version..."
    
    # Launch the new app with admin privileges
    $newExePath = Join-Path "{exe_dir}" "Monitor.exe"
    Start-Process -FilePath $newExePath -Verb RunAs
    
    # Remove script file
    Start-Sleep -Seconds 1
    Remove-Item -Path "{update_script_path}" -Force -ErrorAction SilentlyContinue
    
    Write-Host "Update completed!"
}} catch {{
    Write-Host "Error during update: $_"
    Read-Host "Press Enter to exit"
}}
"""
    
    try:
        with open(update_script_path, "w", encoding='utf-8') as script_file:
            script_file.write(powershell_script_content)
        
        # Execute the update script
        subprocess.Popen([
            "powershell", 
            "-ExecutionPolicy", "Bypass", 
            "-File", update_script_path
        ], shell=False)
        
        return True
    except Exception as e:
        print(f"Error during update: {e}")
        return False
