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
    async function sendQuery() {
        const question = $("#question").val().trim();
        if (!question) {
            alert("Please enter a question.");
            return;
        }

        try {
            const response = await fetch("/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` // Include the token
                },
                body: JSON.stringify({ message: question })
            });

            if (response.ok) {
                const result = await response.json();
                appendMessage("Me", question);
                appendMessage("AIbot", result.response);
                $("#question").val(""); // Clear input field
            } else {
                const errorMessage = (await response.json()).error || "An error occurred. Please try again.";
                appendMessage("AIbot", errorMessage);
            }
        } catch (error) {
            console.error("Error sending query:", error);
            appendMessage("AIbot", "An error occurred. Please try again.");
        }
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
