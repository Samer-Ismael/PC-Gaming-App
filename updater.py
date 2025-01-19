import os
import subprocess
import sys
import requests



APP_VERSION = "1.3.0"

def get_latest_tag_name():
    try:
        url = f"https://api.github.com/repos/Samer-Ismael/PC-Gaming-App/releases/latest"

        response = requests.get(url)

        if response.status_code == 200:
            release_data = response.json()

            tag_name = release_data.get("tag_name", "Tag name not found")

            return tag_name
        else:
            return f"Failed to fetch data: {response.status_code}"
    except Exception as e:
        return f"Error occurred: {e}"
    
           
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
    return GITHUB_VERSION != APP_VERSION


def update_app():
    current_exe_path = os.path.join(os.getcwd(), "app.exe")
    
    update_script = os.path.join(os.getcwd(), "update_script.ps1")
    
    powershell_script_content = f'''
    Remove-Item -Path "{current_exe_path}" -Force
    Invoke-WebRequest -Uri "{EXE_URL}" -OutFile "{current_exe_path}"
    Start-Process -FilePath "{current_exe_path}"
    exit
    '''

    with open(update_script, "w") as file:
        file.write(powershell_script_content)

    subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", update_script])

    sys.exit()

if check_update():
    print("Update available. Updating the app...")
    update_app()
else:
    print("No update available. You are running the latest version.")
