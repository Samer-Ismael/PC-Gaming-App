
from flask import app, jsonify
from Services import MemoryManager, DiskManager

ram = MemoryManager()
disk = DiskManager()



# RAM Endpoint
#------------------------------------------------
@app.route("/clear_cache", methods=["POST"])
def clear_cache():
    try:
        ram.clear_cache_mem() 
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Disk Endpoint
#------------------------------------------------

@app.route("/clear_temp_files", methods=["POST"])
def clear_temp_files_route():
    try:
        disk.clear_temp_files()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
