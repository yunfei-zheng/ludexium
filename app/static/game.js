function togglePlay(gameId, isPlaying) {
    const action = isPlaying ? 'play' : 'unplay'; // Determine the action (play/unplay)
    const button = document.getElementById(`button-${gameId}`);
    const gameElement = document.getElementById(`game-${gameId}`);
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Send a POST request to the appropriate endpoint
    fetch(`/${action}/${gameId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Toggle the button text and behavior
            if (isPlaying) {
                button.textContent = 'Remove from My Games List';
                button.setAttribute('onclick', `togglePlay('${gameId}', false)`);
                button.classList.remove('btn-primary');
                button.classList.add('btn-secondary');
            } else {
                button.textContent = 'Add to My Games List';
                button.setAttribute('onclick', `togglePlay('${gameId}', true)`);
                button.classList.remove('btn-secondary');
                button.classList.add('btn-primary');
            }
            // Optionally fade the game element slightly if unplayed and if current user
            if (isCurrentUser) {
                if (!isPlaying) {
                    gameElement.style.opacity = 0.5; // Visual feedback
                } else {
                    gameElement.style.opacity = 1.0; // Restore visibility
                }
            }
            else {
                gameElement.style.opacity = 1.0; // always 1?
            }
            if (data.message) {
                displayFlashMessage(data.message);
            }
        } else {
            // Handle error response
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing your request.');
    });
}