function processForm(e) {
    if (e.preventDefault) e.preventDefault();

    var formData = new FormData(form)

    fetch('/toggle_lock', {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (response.ok) {
        response.json().then(data => {alert(data['lock_status']);});
      } else {
        alert('Form submit failed');
      }
    })
    .catch(error => {
      alert('Error submitting form:' + error);
    });

    return false;
}

var form = document.getElementById("unlock-form");
if (form.attachEvent) {
    form.attachEvent("submit", processForm);
} else {
    form.addEventListener("submit", processForm);
}