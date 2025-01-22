from flask import app, jsonify
import os




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

