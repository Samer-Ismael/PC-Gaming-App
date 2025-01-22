from flask import Flask, render_template, request
import socket
import logging
from werkzeug.serving import WSGIRequestHandler
import webbrowser
import os
from Services.AdminPrivileges import AdminPrivileges
from Services.AppUpdater import AppUpdater

from controllers import metricsController, updateController, cleaningController, audioController, PCController

app = Flask(__name__)


app.register_blueprint(metricsController.bp)
app.register_blueprint(updateController.bp)
app.register_blueprint(cleaningController.bp)
app.register_blueprint(audioController.bp)
app.register_blueprint(PCController.bp)
app.register_blueprint(audioController.bp)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

admin = AdminPrivileges()
update = AppUpdater( repo_owner="Samer-Ismael", repo_name="PC-Gaming-App")

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

try:
    if not admin.is_admin():
        print("Restarting script with administrator privileges...")
        admin.run_as_admin()
except Exception as e:
    print(f"Failed to check or escalate privileges: {e}")
    exit(1)


try:
    if update.check_update():
        print("Updating application...")
        update.update_app()
except Exception as e:
    print(f"Failed to check or apply updates: {e}")



@app.route("/")
def index():
    ip_address = get_ip_address()
    return render_template("index.html", ip_address=ip_address)

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




if __name__ == "__main__":
    ip_address = get_ip_address()
    url = f'http://{ip_address}:5000'

    if not os.environ.get('FLASK_ENV') == 'development' or not os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print(f"Opening browser at {url}")
        webbrowser.open(url)

    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    print("Starting app...")
    app.run(host="0.0.0.0", port=5000, debug=False)