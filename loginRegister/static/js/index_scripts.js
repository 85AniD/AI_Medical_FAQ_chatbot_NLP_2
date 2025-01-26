$(document).ready(function () {
    // Function to send the user's query to the chatbot
    function sendQuery(queryText) {
        const token = localStorage.getItem("jwt_token");
        if (!token) {
            alert("Authentication token is missing. Please log in again.");
            window.location.href = "/login";
            return;
        }

        if (!queryText || !queryText.trim()) {
            alert("Please enter a question.");
            return;
        }

        // Prepare the payload with the correct field name ("question")
        const payload = {
            question: queryText.trim(), // Ensure this matches the backend expectation
        };

        console.log("Data being sent to server:", payload); // Debugging: Log the payload

        // Send the AJAX request to the chatbot endpoint
        $.ajax({
            url: "/chatbot",
            type: "POST",
            contentType: "application/json",
            headers: {
                "Authorization": `Bearer ${token}`, // Include JWT token in the request headers
            },
            data: JSON.stringify(payload), // Ensure the payload is stringified
            success: function (response) {
                appendMessage("Me", queryText);
                appendMessage("AIbot", response.response);
                $("#question").val(""); // Clear the input field
            },
            error: function (xhr, status, error) {
                console.error("Error details:", status, error, xhr.responseText);
                const errorMessage = xhr.responseJSON?.error || "An error occurred. Please try again.";
                appendMessage("AIbot", errorMessage);
            },
        });
    }

    // Function to append a message to the chat history
    function appendMessage(sender, message) {
        const messageHtml = `<p><strong>${sender}:</strong> ${message}</p>`;
        $("#response").append(messageHtml);
        $("#response").scrollTop($("#response")[0].scrollHeight); // Auto-scroll to the latest message
    }

    // Function to check if the JWT token is valid
    function isTokenValid(token) {
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            const now = Math.floor(Date.now() / 1000);
            return payload.exp > now;
        } catch (error) {
            console.error("Invalid token:", error);
            return false;
        }
    }

    // Check if the JWT token is valid on page load
    if (!isTokenValid(localStorage.getItem("jwt_token"))) {
        alert("Your session has expired. Please log in again.");
        window.location.href = "/login";
    }

    // Prevent default form submission and send the query
    $("#chat-form").submit(function (e) {
        e.preventDefault();
        const queryText = $("#question").val();
        sendQuery(queryText);
    });

    // Handle Enter key press in the input field
    $("#question").keypress(function (e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            const queryText = $("#question").val();
            sendQuery(queryText);
        }
    });
});