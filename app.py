from dead_smart import LockController
from dead_smart import DatabaseController
from flask import Flask, send_from_directory, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

@app.route("/toggle_lock", methods=['POST'])
def toggle_lock():
    if request.method == 'POST':
        passcode = request.form['passcode']
        print(passcode)
    return {'lock_status': lock_controller.get_lock_state()}

if __name__ == '__main__':
    global lock_controller, db_controller
    lock_controller = LockController(True)
    db_controller = DatabaseController("dead_smart.db")
    app.run()