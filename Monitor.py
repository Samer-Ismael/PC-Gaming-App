from ctypes import POINTER
from flask import Flask, jsonify, render_template, request, send_from_directory
import socket
import logging
from werkzeug.serving import WSGIRequestHandler
from gpu import get_gpu_metrics
import cpu 
from ram import get_ram_metrics, clear_cache_mem
from disk import get_disk_metrics, clear_temp_files
import updater
import media
import psutil
import webbrowser
import os
import speedtest

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

#-------------------------------------------------------------------------------------
@app.after_request
def log_bad_requests(response):
    if response.status_code not in [200, 304]:
        print(f"Bad Request Logged: {request.method} {request.path} - Status {response.status_code}")
    return response

@app.before_first_request
def startup_message():
    print ("*************************************************************")
    print("\nThe app is running. Closing this window will stop the app.\n")
    
    ip_address = get_ip_address()
    port = 5000
    link = f"http://{ip_address}:{port}"
    clickable_link = f"\033]8;;{link}\033\\{link}\033]8;;\033\\"
    print ("Use this link to open the page: ", clickable_link)
    
    print ("*************************************************************")

    print(r"""           
                   /\     /\
                  {  `---'  }
                  {  O   O  }
                  ~~>  V  <~~
                   \  \|/  /
                    `-----'____
                    /     \    \_
                   {  **   }\  )_\_   _
                   |  \_/  |/ /  \_\_/ )
                    \__/  /(_/     \__/
                      (__/
    """)

@app.route("/")
def index():
    ip_address = get_ip_address()
    return render_template("index.html", ip_address=ip_address)

# speed Test Endpoint
#------------------------------------------------

@app.route("/speed_test" , methods=["GET"])
def speed_test():
    try:
        st = speedtest.Speedtest()
        st.get_closest_servers()

        download_speed = st.download() / 1_000_000  
        upload_speed = st.upload() / 1_000_000
        ping = st.results.ping

        return jsonify({
            "download_speed": f"{download_speed:.2f}",
            "upload_speed": f"{upload_speed:.2f}",
            "ping": f"{ping:.2f}"
        })

    except Exception as e:
        print(f"Error during speed test: {str(e)}")
        return jsonify({"error": str(e)})

# Metrics Endpoint
#------------------------------------------------

@app.route("/metrics/cpu")
def cpu_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        current = cpu_freq.current
        max = cpu_freq.max
        return jsonify({
            "usage": cpu_usage,
            "Frequency-curent": current,
            "Frequency-max": max,
            "temperature": cpu.get_cpu_temperature_metrics(),
        })
    except Exception as e:
        print(f"Error fetching CPU metrics: {e}")
        return jsonify({
            "usage": "Unavailable",
            "Frequency-curent": "Unavailable",
            "Frequency-max": "Unavailable",
            "temperature": "Unavailable",
        }), 500


@app.route("/metrics/ram")
def ram_metrics():
    try:
        ram_metrics = get_ram_metrics()
        return jsonify(ram_metrics)
    except Exception as e:
        print(f"Error fetching RAM metrics: {e}")
        return jsonify({"usage": "Unavailable", "total": "Unavailable", "free": "Unavailable"}), 500


@app.route("/metrics/disk")
def disk_metrics():
    try:
        disk_metrics = get_disk_metrics()
        return jsonify(disk_metrics)
    except Exception as e:
        print(f"Error fetching Disk metrics: {e}")
        return jsonify({"usage": "Unavailable", "free_space": "Unavailable"}), 500


@app.route("/metrics/gpu")
def gpu_metrics():
    try:
        gpu_metrics = get_gpu_metrics()
        return jsonify(gpu_metrics)
    except Exception as e:
        print(f"Error fetching GPU metrics: {e}")
        return jsonify({"name": "Unavailable", "temperature": "Unavailable", "utilization": "Unavailable", "memory_used": "Unavailable", "memory_total": "Unavailable"}), 500

# Audio Endpoint
#------------------------------------------------

from pycaw.pycaw import AudioUtilities  # Ensure this is included
from icon import icon_mapping

def get_audio_sessions():
    """Retrieve all active audio sessions."""
    sessions = AudioUtilities.GetAllSessions()
    session_list = []
    for session in sessions:
        if session.Process:
            # Add session details (name and dummy icon for simplicity)
            session_list.append({
                "name": session.Process.name(),
                "icon": "fas fa-desktop" if session.Process.name() == "System Sounds" else "fab fa-chrome" if "chrome" in session.Process.name().lower() else "fab fa-discord"
            })
    return session_list

def set_volume(app_name, level):
    """Set the volume level for a specific app."""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() == app_name:
            volume = session.SimpleAudioVolume
            if level == 0:  # Mute
                volume.SetMasterVolume(0, None)
            elif level > 0:  # Increase
                current_volume = volume.GetMasterVolume()
                volume.SetMasterVolume(min(current_volume + level, 1.0), None)
            elif level < 0:  # Decrease
                current_volume = volume.GetMasterVolume()
                volume.SetMasterVolume(max(current_volume + level, 0), None)
            return True
    return False

@app.route('/get_audio_sessions', methods=['GET'])
def get_sessions():
    """Endpoint to fetch all audio sessions."""
    sessions = get_audio_sessions()
    
    for session in sessions:
        app_name = session['name']
        session['icon'] = icon_mapping.get(app_name.lower(), "fas fa-question-circle")
        
    return jsonify({"sessions": sessions})

@app.route('/set_volume', methods=['POST'])
def handle_volume():
    """Endpoint to handle volume actions."""
    data = request.json
    app_name = data.get("app_name")
    level = data.get("level")

    if not app_name or level is None:
        return jsonify({"error": "Invalid data"}), 400

    success = set_volume(app_name, level)
    if success:
        return jsonify({"message": f"Volume updated for {app_name}"}), 200
    else:
        return jsonify({"error": f"App {app_name} not found"}), 404

# RAM Endpoint
#------------------------------------------------

@app.route("/clear_cache", methods=["POST"])
def clear_cache():
    try:
        clear_cache_mem() 
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Disk Endpoint
#------------------------------------------------

@app.route("/clear_temp_files", methods=["POST"])
def clear_temp_files_route():
    try:
        clear_temp_files()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Update Endpoint
#------------------------------------------------

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

# System Endpoint
#------------------------------------------------

@app.route('/shutdown', methods=['POST'])
def shutdown():
    os.system("shutdown /s /t 1") 
    return jsonify({"message": "System shutting down"}), 200

@app.route('/restart', methods=['POST'])
def restart():
    os.system("shutdown /r /t 1") 
    return jsonify({"message": "System restarting"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    os.system("shutdown /l")
    return jsonify({"message": "User logged out"}), 200

@app.route('/lock', methods=['POST'])
def lock():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return jsonify({"message": "System locked"}), 200

#-------------------------------------------------------------------------------------

if __name__ == "__main__":
    ip_address = get_ip_address()
    url = f'http://{ip_address}:5000'

    if not os.environ.get('FLASK_ENV') == 'development' or not os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print(f"Opening browser at {url}")
        webbrowser.open(url)

    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    print("Starting app...")
    app.run(host="0.0.0.0", port=5000, debug=False)