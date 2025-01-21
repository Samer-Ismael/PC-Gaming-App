import os
import subprocess
import sys
import requests



APP_VERSION = "1.3.8"

def get_latest_tag_name():
    """
    Fetches the latest release tag from GitHub.
    """
    try:
        url = "https://api.github.com/repos/Samer-Ismael/PC-Gaming-App/releases/latest"
        response = requests.get(url)

        if response.status_code == 200:
            release_data = response.json()
            tag_name = release_data.get("tag_name", None)

            if tag_name:
                return tag_name
            else:
                print("Tag name not found in the release data.")
                return None
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
           
def get_download_url():
    url = "https://api.github.com/repos/Samer-Ismael/PC-Gaming-App/releases/latest"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        release_data = response.json()
        
        if release_data['assets']:
            download_url = release_data['assets'][0]['browser_download_url']
            return download_url
        else:
            print("No assets found in the release.")
    else:
        print(f"Failed to fetch release data. Status code: {response.status_code}")

GITHUB_VERSION = get_latest_tag_name()
EXE_URL = get_download_url()

def check_update():
    return get_latest_tag_name() != APP_VERSION

def update_app():
    """
    Generate a PowerShell script to update the app and execute it.
    """
    latest_version = get_latest_tag_name()  
    exe_url = get_download_url() 
    
    if not exe_url:
        print("Failed to retrieve the download URL. Aborting update.")
        return

    current_exe_path = os.path.join(os.getcwd(), "Monitor.exe")
    update_script_path = os.path.join(os.getcwd(), "update_script.ps1")

    powershell_script_content = f"""
    # Remove the old app
    Remove-Item -Path "{current_exe_path}" -Force

    # Download the new app
    Invoke-WebRequest -Uri "{exe_url}" -OutFile "{current_exe_path}"

    # Launch the new app
    Start-Process -FilePath "{current_exe_path}"

    # Remove script file
    Remove-Item -Path "{update_script_path}" -Force
    # Exit PowerShell
    exit
    """

    try:
        with open(update_script_path, "w") as script_file:
            script_file.write(powershell_script_content)

        subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", update_script_path])
        sys.exit()
    except Exception as e:
        print(f"Error during update: {e}")


if check_update():
    print("Update available. Updating the app...")
    update_app()
else:
    print("You are running the latest version. " + APP_VERSION)