function showSnackbar(message) {
  snackbarMessage.innerHTML = message;
  snackbar.open();
}

// Initialize Material Design Components
document.addEventListener('DOMContentLoaded', function () {
  window.snackbar = new mdc.snackbar.MDCSnackbar(document.getElementById('snackbar'));
  window.snackbarMessage = document.getElementById('snackbar_text');
  window.buttons = [].map.call(document.querySelectorAll('.mdc-button'), function(el) {
    return new mdc.ripple.MDCRipple(el);
  });
});