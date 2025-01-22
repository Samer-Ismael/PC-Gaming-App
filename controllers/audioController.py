from flask import app, jsonify
from Services import AudioController


audio = AudioController()

@app.route('/volume/increase', methods=['POST'])
def increase_volume():
    try:
        audio.press_volume_key(0xAF, 2)  # VK_VOLUME_UP
        return jsonify({"message": "Volume increased successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/decrease', methods=['POST'])
def decrease_volume():
    try:
        audio.press_volume_key(0xAE, 2)  # VK_VOLUME_DOWN
        return jsonify({"message": "Volume decreased successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/mute', methods=['POST'])
def mute():
    try:
        endpoint = audio.get_audio_endpoint()
        endpoint.SetMute(1, None)  # 1 = Mute
        return jsonify({"message": "Volume muted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/volume/unmute', methods=['POST'])
def unmute():
    try:
        endpoint = audio.get_audio_endpoint()
        endpoint.SetMute(0, None)  # 0 = Unmute
        return jsonify({"message": "Volume unmuted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
