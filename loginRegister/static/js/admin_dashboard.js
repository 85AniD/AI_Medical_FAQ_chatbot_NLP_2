function modify_user(userId) {
    const newUsername = prompt("Enter new username:");
    const newEmail = prompt("Enter new email:");
    if (!newUsername || !newEmail) {
        alert("Both username and email are required!");
        return;
    }

    fetch(`/admin/modify_user/${userId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: newUsername,
            email: newEmail,
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.error) {
            alert(`Error: ${data.error}`);
        } else {
            alert(data.message);
            location.reload(); // Reload the page to reflect changes
        }
    })
    .catch((error) => console.error("Error:", error));
}

function delete_user(userId) {
    if (!confirm("Are you sure you want to delete this user?")) {
        return;
    }

    fetch(`/admin/delete_user/${userId}`, {
        method: "DELETE",
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.error) {
            alert(`Error: ${data.error}`);
        } else {
            alert(data.message);
            location.reload(); // Reload the page to reflect changes
        }
    })
    .catch((error) => console.error("Error:", error));
}
