function displayFlashMessage(message) {
    const flashMessageContainer = document.getElementById('flash-message-container');

    const flashMessageDiv = document.createElement('div');
    flashMessageDiv.classList.add('alert');
    flashMessageDiv.classList.add('alert-info');
    flashMessageDiv.textContent = message;

    flashMessageContainer.appendChild(flashMessageDiv);

    // Auto-dismiss the flash message after 5 seconds
    setTimeout(() => {
        flashMessageDiv.style.display = 'none';
    }, 5000);
}