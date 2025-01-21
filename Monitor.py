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
        {       }\  )_\_   _
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

@app.route('/volume/increase', methods=['POST'])
def increase_volume():
    try:
        media.press_volume_key(0xAF, 2)  # VK_VOLUME_UP
        return jsonify({"message": "Volume increased successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/decrease', methods=['POST'])
def decrease_volume():
    try:
        media.press_volume_key(0xAE, 2)  # VK_VOLUME_DOWN
        return jsonify({"message": "Volume decreased successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/mute', methods=['POST'])
def mute():
    try:
        endpoint = media.get_audio_endpoint()
        endpoint.SetMute(1, None)  # 1 = Mute
        return jsonify({"message": "Volume muted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/unmute', methods=['POST'])
def unmute():
    try:
        endpoint = media.get_audio_endpoint()
        endpoint.SetMute(0, None)  # 0 = Unmute
        return jsonify({"message": "Volume unmuted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# RAM Endpoint
#------------------------------------------------

@app.route("/clear_cache", methods=["POST"])
def clear_cache():
    try:
        clear_cache_mem() 
        return jsonify({"message": "Standby memory cleared successfully."}), 200  
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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