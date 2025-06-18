function sendUnlockCommand() {
    showSnackbar('Unlocking door...');
    fetch('/unlock', {
      method: 'GET',
      credentials: 'include'
    })
    .then(response => {
      if (response.ok) {
        showSnackbar('Unlocked the door.');
      } else if (response.status === 403) {
        showSnackbar('Authentication error. Try logging in again.');
      } else {
        showSnackbar('There was a communication error.');
      }
    })
    .catch(error => {
      showSnackbar('Error sending command:' + error);
    });
  }
  
  function sendLockCommand() {
    showSnackbar('Locking door...');
    fetch('/lock', {
      method: 'GET',
      credentials: 'include'
    })
    .then(response => {
      if (response.ok) {
        showSnackbar('Locked the door.');
      } else if (response.status === 403) {
        showSnackbar('Authentication error. Try logging in again.');
      } else {
        showSnackbar('There was a communication error.');
      }
    })
    .catch(error => {
      showSnackbar('Error sending command:' + error);
    });
  }

  function isAuthenticated() {
    fetch('/auth/test', {
      method: 'GET',
      credentials: 'include'
    })
    .then(response => {
      if (response.ok) {
        return True
      } else if (response.status === 403) {
        return False
      } else {
        return False
      }
    })
    .catch(error => {
      showSnackbar('Error sending command:' + error);
    });
  }

  addEventListener("focus", (event) => {
    if (!isAuthenticated()) {
      location.reload(true) // true bypasses cache
    }
  })