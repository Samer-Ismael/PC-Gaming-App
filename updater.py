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
        
        for asset in release_data['assets']:
            if asset['name'] == 'app.exe': 
                download_url = asset['browser_download_url']

                return download_url
        print("EXE file not found in assets.")
    else:
        print(f"Failed to fetch release data. Status code: {response.status_code}")



GITHUB_VERSION = get_latest_tag_name()
EXE_URL = get_download_url()

def check_update():
    return GITHUB_VERSION != APP_VERSION


