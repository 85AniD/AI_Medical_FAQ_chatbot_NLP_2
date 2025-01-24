function modify_user(user_id) {
    const new_username = prompt("Enter the new username:");
    const new_email = prompt("Enter the new email:");

    if (!new_username || !new_email) {
        alert("Username and email are required!");
        return;
    }

    console.log(`Modifying user ${user_id} with username: ${new_username}, email: ${new_email}`);

    fetch(`/admin/modify_user/${user_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'  // Include CSRF token if needed
        },
        body: JSON.stringify({
            username: new_username,
            email: new_email
        })
    })
    .then(response => {
        console.log("Modify user response:", response);
        if (response.ok) {
            alert("User modified successfully!");
            window.location.reload();
        } else {
            response.json().then(data => {
                alert(`Error: ${data.error}`);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred while modifying the user.");
    });
}

function delete_user(user_id) {
    if (!confirm("Are you sure you want to delete this user?")) {
        return;
    }

    console.log(`Deleting user ${user_id}`);

    fetch(`/admin/delete_user/${user_id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'  // Include CSRF token if needed
        }
    })
    .then(response => {
        console.log("Delete user response:", response);
        if (response.ok) {
            alert("User deleted successfully!");
            window.location.reload();
        } else {
            response.json().then(data => {
                alert(`Error: ${data.error}`);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred while deleting the user.");
    });
}