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

const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
document.getElementById('themeToggleLink').addEventListener('click', async (event) => {
    // Prevent the default link action
    event.preventDefault();

    try {
        const response = await fetch('/toggle-theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        });

        if (!response.ok) {
            throw new Error('Failed to toggle theme');
        }

        const data = await response.json();
        const newTheme = data.theme;

        // Update the theme dynamically by toggling the class
        if (newTheme === "dark") {
            // this edits the html (root)
            document.documentElement.classList.add("dark-mode");
            document.documentElement.classList.remove("light-mode");
        } else {
            document.documentElement.classList.add("light-mode");
            document.documentElement.classList.remove("dark-mode");
        }

        //console.log(`Theme changed to: ${newTheme}`);
    } catch (error) {
        console.error('Error toggling theme:', error);
        alert('An error occurred while processing your request.');
    }
});