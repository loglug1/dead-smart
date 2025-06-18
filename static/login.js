// Initialize Material Design Components
document.addEventListener('DOMContentLoaded', function () {
    window.passcodeField = new mdc.textField.MDCTextField(document.getElementById('passcode')); // Passcode Form Field
    window.buttons = [].map.call(document.querySelectorAll('.mdc-button'), function(el) {
      return new mdc.ripple.MDCRipple(el);
    });
    window.fabRipple = new mdc.ripple.MDCRipple(document.querySelector('.mdc-fab')); // Biometrics Button

    // Availability of `window.PublicKeyCredential` means WebAuthn is usable.  
    // `isUserVerifyingPlatformAuthenticatorAvailable` means the feature detection is usable.  
    // `isConditionalMediationAvailable` means the feature detection is usable.  
    if (window.PublicKeyCredential &&  
      PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable &&  
      PublicKeyCredential.isConditionalMediationAvailable) {  
    // Check if user verifying platform authenticator is available.  
    Promise.all([  
      PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable(),  
      PublicKeyCredential.isConditionalMediationAvailable(),  
    ]).then(results => {  
      if (results.every(r => r === true)) {  
          document.getElementById("passkey-login-button").style.display = "block"
      } else {
          showSnackbox("Passkey support unavailable.");
      }
    });  
    }
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

async function getAuthOptions() {
  try {
    const response = await fetch('/login/auth_options', {
      method: 'get',
      credentials: 'same-origin'
    });

    if (response.ok) {
      showSnackbar("Loading passkeys...");
      const data = await response.json();
      return data;
    } else if (response.status === 404) {
      showSnackbar('No available credentials on server.');
      return {};
    } else {
      showSnackbar('Error fetching available credentials from server.');
      return {};
    }
  } catch (error) {
    showSnackbar('Error fetching credentials: ' + error);
    return {};
  }
}

async function passkeyLogin() {
    const authOptions = await getAuthOptions();
    const options = PublicKeyCredential.parseRequestOptionsFromJSON(authOptions);
    if (options == {}) {
	return;
    }
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

function processLoginForm(e) {
    if (e.preventDefault) e.preventDefault();

    if (e.submitter == null) return;
	
    var formData = new FormData(form);
    formData.append(e.submitter.name, e.submitter.value);

    // console.log(formData.getAll('lock_action'));

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
