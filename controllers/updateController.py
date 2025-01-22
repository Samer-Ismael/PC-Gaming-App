from flask import app, jsonify
from Services import AppUpdater


updater = AppUpdater(repo_owner="Samer-Ismael", repo_name="PC-Gaming-App")

@app.route('/get-app-version', methods=['GET'])
def get_app_version():
    """
    Endpoint to retrieve the current app version.
    """
    return jsonify({'version': updater.APP_VERSION})


@app.route('/check-update', methods=['GET'])
def check_update():
    """
    Endpoint to check if an update is available.
    """
    is_update_available = updater.check_update()
    return jsonify(is_update_available)


@app.route('/update', methods=['POST'])
def update():
    """
    Endpoint to trigger the update process.
    """
    try:        
        updater.update_app()
        return jsonify({'status': 'Updating...'}), 200
    except Exception as e:
        return jsonify({'status': f'Error during update: {e}'}), 500
