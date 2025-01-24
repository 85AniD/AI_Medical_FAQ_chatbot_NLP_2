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

    // Get the JWT token from localStorage
    const token = localStorage.getItem("jwt_token");
    console.log("JWT Token:", token);
    
    // Redirect to login if the token is invalid
    if (!isTokenValid(token)) {
        alert("Your session has expired. Please log in again.");
        window.location.href = "/login";
        return; // Ensure script stops here
    }

    // Send a query to the chatbot
    async function sendQuery() {
        const question = $("#question").val().trim();
    
        // Validate the presence of a valid token and question
        if (!token) {
            alert("Session expired. Please log in again.");
            window.location.href = "/login";
            return;
        }
    
        if (!question) {
            alert("Please enter a question.");
            return;
        }
    
        try {
            console.log("Sending request to /chatbot with payload:", { subject: "chat", message: question });
    
            const response = await fetch("/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ subject: "chat", message: question }) // Include the subject field
            });
    
            console.log("Received response status:", response.status);
    
            if (response.ok) {
                const result = await response.json();
                console.log("Response data:", result);
                appendMessage("Me", question);
                appendMessage("AIbot", result.response);
                $("#question").val(""); // Clear input field
            } else {
                const errorData = await response.json();
                console.error("Error data:", errorData);
                const errorMessage = errorData.error || "An error occurred. Please try again.";
                appendMessage("AIbot", errorMessage);
            }
        } catch (error) {
            console.error("Error sending query:", error);
            appendMessage("AIbot", "An error occurred while connecting to the server.");
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