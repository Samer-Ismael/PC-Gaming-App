"""
PC Gaming App - Main Flask Application
Modernized backend with better error handling, structure, and performance
"""
from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.serving import WSGIRequestHandler
import socket
import logging
import os
import sys
import ctypes
import webbrowser

from config import (
    SERVER_HOST, SERVER_PORT, DEBUG, LIB_FOLDER,
    APP_VERSION
)
from utils.logger import setup_logger
from utils.errors import handle_api_errors
from utils.cache import metrics_cache

# Check for admin privileges and request if needed
def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges."""
    if sys.frozen:
        # If running as exe, use the exe path
        script = sys.executable
    else:
        # If running as script, use the script path
        script = sys.argv[0]
    params = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()

# Request admin privileges on startup
if not is_admin():
    print("Requesting administrator privileges...")
    run_as_admin()

print("Running with administrator privileges.")

# Import metric modules
from gpu import get_gpu_metrics
import cpu
from ram import get_ram_metrics, clear_cache_mem
from disk import get_disk_metrics, clear_temp_files
import updater
import media
import psutil

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logger = setup_logger('PCGamingApp')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Try to import speedtest, handle gracefully if not available or incompatible
try:
    import speedtest
    SPEEDTEST_CLI_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError) as e:
    SPEEDTEST_CLI_AVAILABLE = False

# Import custom speed test (always available)
try:
    from speedtest_custom import run_speed_test
    SPEEDTEST_AVAILABLE = True
except ImportError as e:
    SPEEDTEST_AVAILABLE = False
    logger.warning(f"Custom speed test not available: {e}")


def get_ip_address() -> str:
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        logger.warning(f"Could not determine IP address: {e}")
        return '127.0.0.1'


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(LIB_FOLDER, 'cpu.png')


@app.after_request
def log_bad_requests(response):
    """Log non-200 responses"""
    if response.status_code not in [200, 304]:
        logger.warning(f"Bad Request: {request.method} {request.path} - Status {response.status_code}")
    return response


@app.route("/")
def index():
    """Main page route"""
    ip_address = get_ip_address()
    return render_template("index.html", ip_address=ip_address, version=APP_VERSION)


# ==================== METRICS ENDPOINTS ====================

@app.route("/metrics/cpu")
@handle_api_errors
def cpu_metrics():
    """Get CPU metrics with caching"""
    cached = metrics_cache.get('cpu')
    if cached:
        return jsonify(cached)
    
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        current = cpu_freq.current if cpu_freq else None
        max_freq = cpu_freq.max if cpu_freq else None
        
        temperature = cpu.get_cpu_temperature_metrics()
        
        data = {
            "usage": round(cpu_usage, 2),
            "Frequency-curent": round(current, 2) if current else "N/A",
            "Frequency-max": round(max_freq, 2) if max_freq else "N/A",
            "temperature": temperature if temperature else "N/A",
        }
        
        metrics_cache.set('cpu', data)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching CPU metrics: {e}")
        return jsonify({
            "usage": "Unavailable",
            "Frequency-current": "Unavailable",
            "Frequency-max": "Unavailable",
            "temperature": "Unavailable",
        }), 500


@app.route("/metrics/ram")
@handle_api_errors
def ram_metrics():
    """Get RAM metrics with caching"""
    cached = metrics_cache.get('ram')
    if cached:
        return jsonify(cached)
    
    try:
        ram_metrics_data = get_ram_metrics()
        metrics_cache.set('ram', ram_metrics_data)
        return jsonify(ram_metrics_data)
    except Exception as e:
        logger.error(f"Error fetching RAM metrics: {e}")
        return jsonify({
            "usage": "Unavailable",
            "total": "Unavailable",
            "free": "Unavailable"
        }), 500


@app.route("/metrics/disk")
@handle_api_errors
def disk_metrics():
    """Get disk metrics with caching"""
    cached = metrics_cache.get('disk')
    if cached:
        return jsonify(cached)
    
    try:
        disk_metrics_data = get_disk_metrics()
        metrics_cache.set('disk', disk_metrics_data)
        return jsonify(disk_metrics_data)
    except Exception as e:
        logger.error(f"Error fetching Disk metrics: {e}")
        return jsonify({
            "usage": "Unavailable",
            "free_space": "Unavailable",
            "read_speed": "Unavailable",
            "write_speed": "Unavailable"
        }), 500


@app.route("/metrics/gpu")
@handle_api_errors
def gpu_metrics():
    """Get GPU metrics with caching"""
    cached = metrics_cache.get('gpu')
    if cached:
        return jsonify(cached)
    
    try:
        gpu_metrics_data = get_gpu_metrics()
        metrics_cache.set('gpu', gpu_metrics_data)
        return jsonify(gpu_metrics_data)
    except Exception as e:
        logger.error(f"Error fetching GPU metrics: {e}")
        return jsonify({
            "name": "Unavailable",
            "temperature": "Unavailable",
            "utilization": "Unavailable",
            "memory_used": "Unavailable",
            "memory_total": "Unavailable"
        }), 500


# ==================== SPEED TEST ENDPOINT ====================

@app.route("/speed_test", methods=["GET"])
@handle_api_errors
def speed_test_endpoint():
    """Run internet speed test using custom implementation"""
    if not SPEEDTEST_AVAILABLE:
        return jsonify({
            "error": "Speed test feature is not available.",
            "available": False
        }), 503
    
    try:
        # Use custom speed test implementation
        results = run_speed_test()
        
        if results["download_speed"] == 0 and results["upload_speed"] == 0:
            return jsonify({
                "error": "Speed test failed. Please check your internet connection and try again.",
                "available": True
            }), 500
        
        return jsonify({
            "download_speed": f"{results['download_speed']:.2f}",
            "upload_speed": f"{results['upload_speed']:.2f}",
            "ping": f"{results['ping']:.2f}",
            "available": True
        })
    except Exception as e:
        logger.error(f"Error during speed test: {str(e)}")
        return jsonify({
            "error": f"Speed test failed: {str(e)}. Please try again later.",
            "available": True
        }), 500


# ==================== AUDIO ENDPOINTS ====================

from pycaw.pycaw import AudioUtilities
from icon import icon_mapping


def get_audio_sessions():
    """Retrieve all active audio sessions"""
    try:
        sessions = AudioUtilities.GetAllSessions()
        session_list = []
        for session in sessions:
            if session.Process:
                app_name = session.Process.name()
                volume = session.SimpleAudioVolume
                session_list.append({
                    "name": app_name,
                    "icon": icon_mapping.get(app_name.lower(), "fas fa-volume-up"),
                    "volume": round(volume.GetMasterVolume() * 100, 0) if volume else 0,
                    "muted": volume.GetMute() if volume else False
                })
        return session_list
    except Exception as e:
        logger.error(f"Error getting audio sessions: {e}")
        return []


def set_volume(app_name: str, level: float):
    """Set the volume level for a specific app"""
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == app_name:
                volume = session.SimpleAudioVolume
                if level == 0:  # Mute
                    volume.SetMute(1, None)
                elif level > 0:  # Set specific volume
                    volume.SetMute(0, None)
                    volume.SetMasterVolume(min(level, 1.0), None)
                return True
        return False
    except Exception as e:
        logger.error(f"Error setting volume: {e}")
        return False


@app.route('/get_audio_sessions', methods=['GET'])
@handle_api_errors
def get_sessions():
    """Endpoint to fetch all audio sessions"""
    sessions = get_audio_sessions()
    return jsonify({"sessions": sessions})


@app.route('/set_volume', methods=['POST'])
@handle_api_errors
def handle_volume():
    """Endpoint to handle volume actions"""
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


# ==================== SYSTEM ACTION ENDPOINTS ====================

@app.route("/clear_cache", methods=["POST"])
@handle_api_errors
def clear_cache():
    """Clear system cache/memory"""
    try:
        clear_cache_mem()
        metrics_cache.clear()  # Clear metrics cache
        return jsonify({"status": "success", "message": "Memory cache cleared successfully"}), 200
    except PermissionError as e:
        logger.warning(f"Permission denied clearing cache: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "requires_admin": True
        }), 403
    except FileNotFoundError as e:
        logger.error(f"File not found clearing cache: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/clear_temp_files", methods=["POST"])
@handle_api_errors
def clear_temp_files_route():
    """Clear temporary files"""
    try:
        results = clear_temp_files()
        message = (
            f"Cleared {results['total_deleted']} files. "
            f"Skipped {results['total_skipped']} files in use."
        )
        if results['total_errors'] > 0:
            message += f" {results['total_errors']} errors occurred."
        
        return jsonify({
            "status": "success",
            "message": message,
            "details": results
        }), 200
    except Exception as e:
        logger.error(f"Error clearing temp files: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== UPDATE ENDPOINTS ====================

@app.route('/get-app-version', methods=['GET'])
def get_app_version():
    """Get current app version"""
    return jsonify({'version': APP_VERSION})


@app.route('/check-update', methods=['GET'])
@handle_api_errors
def check_update():
    """Check if an update is available"""
    try:
        is_update_available = updater.check_update()
        return jsonify(is_update_available)
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/update', methods=['POST'])
@handle_api_errors
def update():
    """Trigger the update process"""
    try:
        updater.update_app()
        return jsonify({'status': 'Updating...'}), 200
    except Exception as e:
        logger.error(f"Error during update: {e}")
        return jsonify({'status': f'Error during update: {e}'}), 500


# ==================== SYSTEM CONTROL ENDPOINTS ====================

@app.route('/shutdown', methods=['POST'])
@handle_api_errors
def shutdown():
    """Shutdown the system"""
    try:
        os.system("shutdown /s /t 1")
        return jsonify({"message": "System shutting down"}), 200
    except Exception as e:
        logger.error(f"Error shutting down: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/restart', methods=['POST'])
@handle_api_errors
def restart():
    """Restart the system"""
    try:
        os.system("shutdown /r /t 1")
        return jsonify({"message": "System restarting"}), 200
    except Exception as e:
        logger.error(f"Error restarting: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/logout', methods=['POST'])
@handle_api_errors
def logout():
    """Logout current user"""
    try:
        os.system("shutdown /l")
        return jsonify({"message": "User logged out"}), 200
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lock', methods=['POST'])
@handle_api_errors
def lock():
    """Lock the system"""
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return jsonify({"message": "System locked"}), 200
    except Exception as e:
        logger.error(f"Error locking system: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/exit', methods=['POST'])
@handle_api_errors
def exit_app():
    """Close/exit the application (terminates the exe process)"""
    try:
        logger.info("Application exit requested")
        # Schedule exit in a separate thread to allow response to be sent
        import threading
        def force_exit():
            import time
            time.sleep(0.5)  # Give time for response to be sent
            # Force exit - this will terminate the exe process
            os._exit(0)
        
        shutdown_thread = threading.Thread(target=force_exit)
        shutdown_thread.daemon = True
        shutdown_thread.start()
        
        return jsonify({"message": "Application closing..."}), 200
    except Exception as e:
        logger.error(f"Error exiting application: {e}")
        # Force exit as fallback
        import threading
        threading.Timer(0.5, lambda: os._exit(0)).start()
        return jsonify({"message": "Application closing..."}), 200


# ==================== MEDIA ENDPOINTS ====================

@app.route('/media/<command>', methods=['POST'])
@handle_api_errors
def execute_command(command):
    """Execute media control commands"""
    valid_commands = ['prev_track', 'play_pause', 'next_track']
    
    if command not in valid_commands:
        return jsonify({"error": "Invalid command"}), 400
    
    try:
        media.send_media_key(command)
        return jsonify({"message": f"Command '{command}' executed successfully!"})
    except Exception as e:
        logger.error(f"Error executing media command: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== STARTUP ====================

def startup_message():
    """Display startup message with IP and port"""
    print("=" * 60)
    print("\n🚀 PC Gaming App is running!")
    print("   Closing this window will stop the app.\n")
    
    ip_address = get_ip_address()
    port = SERVER_PORT
    link = f"http://{ip_address}:{port}"
    
    print(f"📱 Access on your phone: {link}")
    print(f"💻 Access on this PC: http://localhost:{port}")
    print("=" * 60)
    
    # Check for updates on startup
    print("\n🔍 Checking for updates...")
    try:
        if updater.check_update():
            latest_version = updater.get_latest_tag_name()
            print(f"⚠️  UPDATE AVAILABLE!")
            print(f"   Current version: {APP_VERSION}")
            print(f"   Latest version: {latest_version}")
            print(f"   Check the web interface to update.\n")
        else:
            print(f"✅ You are running the latest version ({APP_VERSION})\n")
    except Exception as e:
        logger.warning(f"Could not check for updates on startup: {e}")
        print(f"⚠️  Could not check for updates. Will check in web interface.\n")
    
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


if __name__ == "__main__":
    startup_message()
    
    ip_address = get_ip_address()
    url = f'http://{ip_address}:{SERVER_PORT}'
    
    # Only open browser if not in development mode
    if not DEBUG or not os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
    
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    logger.info(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
