import threading
from flask import Flask, jsonify, render_template, request
import socket
import logging
from werkzeug.serving import WSGIRequestHandler
from gpu import get_gpu_metrics, init_gpu
import cpu 
from ram import get_ram_metrics, clear_cache_mem
from disk import get_disk_metrics, clear_temp_files
import psutil
import webbrowser
import os
import ctypes

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

gpu_available = init_gpu()
print(f"GPU Available: {gpu_available}")

def press_volume_key(key_code, times=1):
    """Simulates pressing a volume key."""
    for _ in range(times):
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key release

def get_cpu_temperature():
    return cpu.get_temperatures()

@app.after_request
def log_bad_requests(response):
    if response.status_code not in [200, 304]:
        print(f"Bad Request Logged: {request.method} {request.path} - Status {response.status_code}")
    return response

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

@app.before_first_request
def startup_message():
    print("\nThe app is running. Closing this window will stop the app.\n")

#-------------------------------------------------------------------------------------
@app.route("/")
def index():
    ip_address = get_ip_address()
    return render_template("index.html", ip_address=ip_address)

@app.route("/metrics")
def metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_metrics = get_ram_metrics()
        disk_metrics = get_disk_metrics()
        gpu_metrics = get_gpu_metrics()

        return jsonify({
            "cpu": {
                "usage": cpu_usage,
                "temperature": get_cpu_temperature(),
            },
            "ram": ram_metrics,
            "disk": disk_metrics,
            "gpu": gpu_metrics,
        })
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return jsonify({
            "cpu": {"usage": "Unavailable", "temperature": "Unavailable"},
            "ram": {"usage": "Unavailable", "total": "Unavailable", "free": "Unavailable"},
            "disk": {"usage": "Unavailable", "free_space": "Unavailable"},
            "gpu": {"name": "Unavailable", "temperature": "Unavailable", "utilization": "Unavailable"},
        })

@app.route('/volume/increase', methods=['POST'])
def increase_volume():
    try:
        press_volume_key(0xAF, 2)  # VK_VOLUME_UP
        return jsonify({"message": "Volume increased successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/decrease', methods=['POST'])
def decrease_volume():
    try:
        press_volume_key(0xAE, 2)  # VK_VOLUME_DOWN
        return jsonify({"message": "Volume decreased successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/mute', methods=['POST'])
def mute():
    try:
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x319, 0, 0x80000)
        return jsonify({"message": "Volume muted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/unmute', methods=['POST'])
def unmute():
    try:
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x319, 0, 0x80000)
        return jsonify({"message": "Volume unmuted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/clear_cache", methods=["POST"])
def clear_cache():
    try:
        clear_cache_mem() 
        return jsonify({"message": "Standby memory cleared successfully."}), 200  
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/clear_temp_files", methods=["POST"])
def clear_temp_files_route():
    try:
        clear_temp_files()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
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
