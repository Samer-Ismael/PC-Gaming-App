import requests


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
            
APP_VERSION = "1.3.0"
GITHUB_VERSION = get_latest_tag_name()


def check_update():
    return GITHUB_VERSION != APP_VERSION