// Initialize Material Design Components
document.addEventListener('DOMContentLoaded', function () {
    window.passcodeField = new mdc.textField.MDCTextField(document.getElementById('passcode'));
    window.snackbar = new mdc.snackbar.MDCSnackbar(document.getElementById('snackbar'));
    window.snackbarMessage = document.getElementById('snackbar_text');
    window.buttons = [].map.call(document.querySelectorAll('.mdc-button'), function(el) {
      return new mdc.ripple.MDCRipple(el);
    });

    passkeyLogin()
});

function serializeCredential(cred) {
    return {
        id: cred.id,
        rawId: arrayBufferToBase64url(cred.rawId),
        response: {
            authenticatorData: arrayBufferToBase64url(cred.response.authenticatorData),
            clientDataJSON: arrayBufferToBase64url(cred.response.clientDataJSON),
            signature: arrayBufferToBase64url(cred.response.signature),
            userHandle: arrayBufferToBase64url(cred.response.userHandle)
        },
        type: cred.type,
    };
}

function arrayBufferToBase64url(buffer) {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

async function passkeyLogin() {
    const options = PublicKeyCredential.parseRequestOptionsFromJSON(authOptions)
    window.temp = options;
    let credential = await navigator.credentials.get({
    publicKey: options
    });
    console.log(credential);
    const serialized = serializeCredential(credential);
    const result = JSON.stringify(serialized);

    // Encode and send the credential to the server for verification.  
    fetch('/auth/passkey', {
        method: 'post',
        credentials: 'same-origin',
        body: result
    }).then(response => {
        if (response.ok) {
          response.json().then(data => { window.location.replace(data['url']); });
        } else if (response.status === 403) {
            response.json().then(data => { showSnackbar(data['auth_status']); });
        } else {
          showSnackbar('Form submit failed');
        }
      })
      .catch(error => {
        showSnackbar('Error submitting form:' + error);
      });
}

function showSnackbar(message) {
    snackbarMessage.innerHTML = message;
    snackbar.open();
}

function processLoginForm(e) {
    if (e.preventDefault) e.preventDefault();

    if (e.submitter == null) return;
	
    var formData = new FormData(form);
    formData.append(e.submitter.name, e.submitter.value);

    console.log(formData.getAll('lock_action'));

    fetch('/auth/passcode', {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (response.ok) {
        response.json().then(data => { window.location.replace(data['url']); });
      } else if (response.status === 403) {
        showSnackbar('Invalid Passcode.');
      } else {
        showSnackbar('Form submit failed');
      }
    })
    .catch(error => {
      showSnackbar('Error submitting form:' + error);
    });

    return false;
}

var form = document.getElementById("login-form");
if (form.attachEvent) {
    form.attachEvent("submit", processLoginForm);
} else {
    form.addEventListener("submit", processLoginForm);
}