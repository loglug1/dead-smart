function processLockControlForm(e) {
    if (e.preventDefault) e.preventDefault();

    if (e.submitter == null) return;
	
    var formData = new FormData(form);
    formData.append(e.submitter.name, e.submitter.value);

    console.log(formData.getAll('lock_action'));

    fetch('/control_lock', {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (response.ok) {
        response.json().then(data => {alert('Locked: ' + data['lock_status'] + ' User: ' +data['user']);});
      } else {
        alert('Form submit failed');
      }
    })
    .catch(error => {
      alert('Error submitting form:' + error);
    });

    return false;
}

var form = document.getElementById("lock-control-form");
if (form.attachEvent) {
    form.attachEvent("submit", processLockControlForm);
} else {
    form.addEventListener("submit", processLockControlForm);
}
