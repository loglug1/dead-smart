document.addEventListener('DOMContentLoaded', function () {
  window.passcodeField = new mdc.textField.MDCTextField(document.getElementById('new-passcode')); // New Passcode Form Field
});

function processChangeForm(e) {
    if (e.preventDefault) e.preventDefault();

    if (e.submitter == null) return;
	
    var formData = new FormData(form);
    formData.append(e.submitter.name, e.submitter.value);

    fetch('/auth/set/passcode', {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (response.ok) {
        showSnackbar('Passcode changed successfully!');
      } else if (response.status === 403) {
        showSnackbar('Authentication error. Try logging in again.');
      } else {
        showSnackbar('Form submit failed');
      }
    })
    .catch(error => {
      showSnackbar('Error submitting form:' + error);
    });

    return false;
}

var form = document.getElementById("change-passcode-form");
if (form.attachEvent) {
    form.attachEvent("submit", processChangeForm);
} else {
    form.addEventListener("submit", processChangeForm);
}