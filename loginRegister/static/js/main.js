$(document).ready(function () {
    // Check if the JWT token is valid
    function isTokenValid(token) {
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split(".")[1])); // Decode JWT payload
            const now = Math.floor(Date.now() / 1000); // Current timestamp
            return payload.exp > now; // Check if token is expired
        } catch (error) {
            console.error("Invalid token:", error);
            return false;
        }
    }

    // Redirect to login if the token is invalid
    const token = localStorage.getItem("jwt_token");
    if (!isTokenValid(token)) {
        alert("Your session has expired. Please log in again.");
        window.location.href = "/login";
    }

    // Send a query to the chatbot
    function sendQuery() {
        const question = $("#question").val().trim();
        if (!question) {
            alert("Please enter a question.");
            return;
        }

        $.ajax({
            type: "POST",
            url: "/chatbot",
            contentType: "application/json",
            headers: {
                "Authorization": `Bearer ${token}` // Include the token
            },
            data: JSON.stringify({ message: question }),
            success: function (result) {
                appendMessage("Me", question);
                appendMessage("AIbot", result.response);
                $("#question").val(""); // Clear input field
            },
            error: function (xhr) {
                const errorMessage = xhr.responseJSON?.error || "An error occurred. Please try again.";
                appendMessage("AIbot", errorMessage);
            }
        });
    }

    // Append a message to the chat history
    function appendMessage(sender, message) {
        const messageHtml = `<p><strong>${sender}:</strong> ${message}</p>`;
        $("#response").append(messageHtml);
        $("#response").scrollTop($("#response")[0].scrollHeight); // Auto-scroll to the bottom
    }

    // Handle form submission
    $("#chat-form").submit(function (e) {
        e.preventDefault();
        sendQuery();
    });

    // Handle Enter key press
    $("#question").keypress(function (e) {
        if (e.which === 13) {
            e.preventDefault();
            sendQuery();
        }
    });
});