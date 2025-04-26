from dead_smart import LockController
from dead_smart import DatabaseController
from flask import Flask, send_from_directory, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Initialize classes used by application
lock_controller = LockController(True)
db_controller = DatabaseController("dead_smart.db")

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

def set_locked_state(state, passcode):
    global db_controller

@app.route("/control_lock", methods=['POST'])
def toggle_lock():
    global lock_controller
    if request.method == 'POST':
        passcode = request.form['passcode']
        action = request.form['lock_action']
        user = db_controller.verify_user(passcode)
        if user == None:
            return {'lock_status': 'Invalid Passcode!'}
        if action == 'unlock':
            lock_controller.unlock()
        else:
            lock_controller.lock()
        return {'user': user, 'lock_status': lock_controller.get_lock_state()}
    return 'Malformed request', 400

if __name__ == '__main__':
    app.run(host="0.0.0.0")
