from flask import app, jsonify
import speedtest

def speed_test():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()

        download_speed = st.download() / 1_000_000  
        upload_speed = st.upload() / 1_000_000 

        return jsonify({
            "download_speed": f"{download_speed:.2f}",
            "upload_speed": f"{upload_speed:.2f}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})
