try:
    from lock_controlleri import LockController
except ImportError as e:
    print("GPIO Library Missing, using simulated lock controller: ", e)
    from fake_lock_controller import LockController
from database_controller import DatabaseController
from flask import Flask, render_template, request, session, redirect, url_for
import webauthn
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, UserVerificationRequirement
from webauthn.helpers.exceptions import InvalidAuthenticationResponse
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlparse
import json
import secrets
import base64

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.secret_key = secrets.token_hex()

trusted_origins = ['https://ds.tri-quad.net','https://localhost:5000', 'https://ds.tri-quad.net:5000']

# Initialize classes used by application
lock_controller = LockController(True)
db_controller = DatabaseController("dead_smart.db")

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("home.html", title="Lock Controls")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    # Generate data to use passkey
    url = urlparse(request.base_url).hostname
    credentials = db_controller.get_credential_data()

    if credentials == None:
        return render_template("login.html", title="Login", auth_options=None)
    
    allowed_credentials = []
    for credential_id in credentials:
        allowed_credentials.append(PublicKeyCredentialDescriptor(id=credential_id[0]))
    auth_options = webauthn.generate_authentication_options(rp_id=url, allow_credentials=allowed_credentials, user_verification=UserVerificationRequirement.REQUIRED)
    session['challenge'] = auth_options.challenge

    return render_template("login.html", title="Login", auth_options=webauthn.options_to_json(auth_options))

@app.route("/auth/passcode", methods=["POST"])
def auth_passcode():
    if 'passcode' in request.form: #passcode login
        passcode = request.form['passcode']
        user = db_controller.verify_user(passcode)
        if user == None:
            return {'lock_status': 'Invalid Passcode!'}, 403
        session['user_id'] = user
        redirect_url = session.pop('redirect', 'home')
        return {'url': url_for(redirect_url)}
    
@app.route("/auth/passkey", methods=["POST"])
def auth_passkey():
    url = urlparse(request.base_url).hostname
    print(json.loads(request.get_data().decode('utf-8'))['id'])
    credential_id = webauthn.base64url_to_bytes(json.loads(request.get_data().decode('utf-8'))['id'])
    credential_auth_data = db_controller.get_credential_auth_data(credential_id)
    if credential_auth_data == None:
        return {'auth_status': 'Credential not found.'}, 403
    key = credential_auth_data[0]
    user_id = credential_auth_data[1]
    sign_count = credential_auth_data[2]
    print(request.get_data().decode('utf-8'))
    try:
        auth_verification = webauthn.verify_authentication_response(credential=request.get_data().decode('utf-8'), expected_challenge=session.pop('challenge', None) , expected_rp_id=url, expected_origin=trusted_origins, credential_public_key=key, credential_current_sign_count=0)
        print(auth_verification)
        db_controller.update_credential_sign_count(credential_id, sign_count + 1)
        redirect_url = session.pop('redirect', 'home')
        session['user_id'] = user_id
        return {'url': url_for(redirect_url)}
    except InvalidAuthenticationResponse as e:
        return {'auth_status': str(e)}, 403

@app.route("/lock")
def lock():
    if 'user_id' not in session:
        return {'error': 'invalid_session'}, 403
    lock_controller.lock()
    return {}, 200

@app.route("/unlock")
def unlock():
    if 'user_id' not in session:
        return {'error': 'invalid_session'}, 403
    lock_controller.unlock()
    return {}, 200

@app.route("/passkeyRegistrationRequest")
def passkey_registration_request():
    if 'user_id' not in session:
        return {'error': 'invalid_session'}, 403
    url = urlparse(request.base_url).hostname
    random_bytes = secrets.token_bytes(32)
    base64_challenge = base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode("ascii")
    user_id = session['user_id']
    user_data = db_controller.get_user_data(user_id)
    name = user_data[0] # 0 = username
    displayName = user_data[1] # 1 = name
    existing_credentials = db_controller.get_credential_data(user_id)
    exclude_credentials = []
    if existing_credentials:
        for credential in existing_credentials:
            exclude_credentials.append({'id': credential[0], 'type': 'public-key'}) # 0 = id
    creation_options = webauthn.generate_registration_options(
        rp_id=url,
        rp_name="Dead Smart",
        user_id=bytes(user_id),
        user_name=name
    )
    session['challenge'] = creation_options.challenge
    return webauthn.options_to_json(creation_options)
    # return {
    #     'challenge': base64_challenge,
    #     'rp': {'name': 'Dead Smart', 'id': url},
    #     'user': {'id': base64.urlsafe_b64encode(bytes(user_id)).rstrip(b'=').decode("ascii"), 'name': name, 'displayName': displayName},
    #     'pubKeyCredParams': [{'alg': -7, 'type': 'public-key'}, {'alg': -257, 'type': 'public-key'}],
    #     #'excludeCredentials': exclude_credentials,
    #     #'authenticatorSelection': {'authenticatorAttachment': 'platform', 'requireResidentKey': True, 'userVerification': 'required'}
    # }, 200

@app.route("/registerPasskey", methods=["POST"])
def register_passkey():
    if 'user_id' not in session:
        return {'error': 'invalid_session'}, 403
    url = urlparse(request.base_url).hostname
    auth_verification = webauthn.verify_registration_response(credential=request.get_data().decode('utf-8'), expected_challenge=session.pop('challenge', None) , expected_rp_id=url, expected_origin=trusted_origins)
    db_controller.save_credential(session['user_id'], auth_verification.credential_public_key, auth_verification.credential_id)
    print(auth_verification)
    return {}

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route("/create-passkey")
def create_passkey():
    if 'user_id' not in session:
        session['redirect'] = 'create_passkey'
        return redirect(url_for('login'))
    return render_template("create-passkey.html", title="Create a Passkey")

@app.route("/test")
def test():
    return urlparse(request.base_url).hostname

if __name__ == '__main__':
    app.run(host="0.0.0.0")#, ssl_context=('cert2.pem', 'privkey2.pem'))
