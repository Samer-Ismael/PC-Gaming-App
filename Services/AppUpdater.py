import os
import subprocess
import sys
import requests

class AppUpdater:
    APP_VERSION = "1.4.1"

    def __init__(self, repo_owner, repo_name):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    def get_latest_tag_name(self):
        """
        Fetches the latest release tag from GitHub.
        """
        try:
            response = requests.get(self.github_api_url)

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

    def get_download_url(self):
        """
        Fetches the download URL for the latest release asset from GitHub.
        """
        try:
            response = requests.get(self.github_api_url)

            if response.status_code == 200:
                release_data = response.json()

                if release_data['assets']:
                    download_url = release_data['assets'][0]['browser_download_url']
                    return download_url
                else:
                    print("No assets found in the release.")
                    return None
            else:
                print(f"Failed to fetch release data. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    def check_update(self):
        """
        Checks if an update is available by comparing the latest tag with the current version.
        """
        latest_version = self.get_latest_tag_name()
        return latest_version and latest_version != self.APP_VERSION

    def update_app(self):
        """
        Generate a PowerShell script to update the app and execute it.
        """
        latest_version = self.get_latest_tag_name()
        exe_url = self.get_download_url()

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
