from flask import app, jsonify
import speedtest


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
