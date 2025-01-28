$(document).ready(function () {
    // Function to send the user's query to the chatbot
    function sendQuery(queryText) {
        if (!queryText.trim()) {
            alert("Please enter a valid question.");
            return;
        }

        // Append the user's message to the chat history
        appendMessage("Me", queryText.trim());

        const payload = { question: queryText.trim() };
        console.log("Payload being sent:", payload); // Log payload

        $.ajax({
            url: "/chatbot",
            type: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            data: JSON.stringify(payload),
            success: function (response) {
                console.log("Chatbot response:", response); // Log response
                // Append the chatbot's response to the chat history
                appendMessage("Ayur", response.response);
            },
            error: function (xhr) {
                console.error("Error details:", xhr.responseText);
                const errorMessage = xhr.responseJSON?.error || "An error occurred. Please try again.";
                // Append the error message to the chat history
                appendMessage("Ayur", errorMessage);
            }
        });
    }

    // Function to append a message to the chat history
    function appendMessage(sender, message) {
        const messageHtml = `
            <div class="chat-message">
                <strong>${sender}:</strong> ${message}
            </div>`;
        $("#response").append(messageHtml);
        $("#response").scrollTop($("#response")[0].scrollHeight); // Auto-scroll to the latest message
    }

    // Logout function
    function logout() {
        window.location.href = "/login"; // Redirect to the login page
    }

    // Bind the logout function to the logout button
    $("#logout-button").on("click", function (e) {
        e.preventDefault();
        logout();
    });

    // Handle form submission
    $("#chat-form").on("submit", function (e) {
        e.preventDefault();
        const queryText = $("#question").val();
        sendQuery(queryText);
        $("#question").val(""); // Clear input after sending
    });

    // Handle Enter key press in the input field
    $("#question").on("keypress", function (e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            const queryText = $("#question").val();
            sendQuery(queryText);
            $("#question").val(""); // Clear input after sending
        }
    });
});