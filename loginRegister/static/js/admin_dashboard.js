// Function to modify a user
function modify_user(user_id) {
    const new_username = prompt("Enter the new username:");
    const new_email = prompt("Enter the new email:");

    // Validate input
    if (!new_username || !new_email) {
        alert("Username and email are required!");
        return;
    }

    // Get the JWT token from localStorage
    const token = localStorage.getItem("jwt_token");
    if (!token) {
        alert("Authentication token is missing. Please log in again.");
        window.location.href = "/login";
        return;
    }

    // Send a POST request to modify the user
    fetch(`/admin/modify_user/${user_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` // Include the token
        },
        body: JSON.stringify({
            username: new_username,
            email: new_email
        })
    })
    .then(response => {
        if (response.ok) {
            alert("User modified successfully!");
            window.location.reload(); // Reload the page to reflect changes
        } else {
            // Handle errors from the server
            response.json().then(data => {
                alert(`Error: ${data.error || "An unknown error occurred."}`);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred while modifying the user. Please try again.");
    });
}

// Function to delete a user
function delete_user(user_id) {
    // Confirm deletion
    if (!confirm("Are you sure you want to delete this user?")) {
        return;
    }

    // Get the JWT token from localStorage
    const token = localStorage.getItem("jwt_token");
    if (!token) {
        alert("Authentication token is missing. Please log in again.");
        window.location.href = "/login";
        return;
    }

    // Send a DELETE request to delete the user
    fetch(`/admin/delete_user/${user_id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` // Include the token
        }
    })
    .then(response => {
        if (response.ok) {
            alert("User deleted successfully!");
            window.location.reload(); // Reload the page to reflect changes
        } else {
            // Handle errors from the server
            response.json().then(data => {
                alert(`Error: ${data.error || "An unknown error occurred."}`);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred while deleting the user. Please try again.");
    });
}

// Attach event listeners to buttons
document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to modify buttons
    document.querySelectorAll('.modify-btn').forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            modify_user(userId);
        });
    });

    // Attach event listeners to delete buttons
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            delete_user(userId);
        });
    });
});