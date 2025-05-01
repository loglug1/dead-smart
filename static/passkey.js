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
        document.getElementById("create-passkey-button").style.display = "block"
    } else {
        showSnackbox("Passkey support unavailable.");
    }
  });  
}

function serializeCredential(cred) {
    return {
        id: cred.id,
        rawId: arrayBufferToBase64url(cred.rawId),
        response: {
            clientDataJSON: arrayBufferToBase64url(cred.response.clientDataJSON),
            attestationObject: arrayBufferToBase64url(cred.response.attestationObject),
        },
        type: cred.type,
        clientExtensionResults: cred.getClientExtensionResults(),
    };
}

function arrayBufferToBase64url(buffer) {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

async function createPasskey() {
    // Fetch an encoded `PubicKeyCredentialCreationOptions` from the server.
    const _options = await fetch('/passkeyRegistrationRequest');

    // Deserialize and decode the `PublicKeyCredentialCreationOptions`.
    const decoded_options = await _options.json()
    const options = PublicKeyCredential.parseCreationOptionsFromJSON(decoded_options);

    // Invoke WebAuthn to create a passkey.
    const credential = await navigator.credentials.create({
        publicKey: options
    });

    // Encode and serialize the `PublicKeyCredential`.
    const serialized = serializeCredential(credential);
    const result = JSON.stringify(serialized);

    // Encode and send the credential to the server for verification.  
    const response = await fetch('/registerPasskey', {
    method: 'post',
    credentials: 'same-origin',
    body: result
    });
}