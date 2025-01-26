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

    // Function to send a query to the chatbot
    function sendQuery() {
        const question = $("#question").val().trim();
    
        // Validate the presence of a valid token
        if (!token) {
            alert("Session expired. Please log in again.");
            window.location.href = "/login";
            return;
        }
    
        // Validate the question input
        if (!question || typeof question !== "string") {
            alert("Please enter a valid question.");
            return;
        }
    
        console.log("Sending payload:", JSON.stringify({ subject: question })); // Debugging
    
        // Send the question to the chatbot endpoint
        $.ajax({
            type: "POST",
            url: "/chatbot",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            data: JSON.stringify({ subject: question }),
            success: function (result) {
                // Append the user's question and chatbot's response to the chat history
                $("#response").append(
                    `<p><strong>Me:</strong> ${question}</p>` +
                    `<p><strong>AIbot:</strong> ${result.response}</p>`
                );
                $("#question").val(""); // Clear the input field
                $('#response').animate({
                    scrollTop: $('#response').prop("scrollHeight")
                }, 500); // Auto-scroll to the bottom
            },
            error: function (xhr, status, error) {
                let errorMessage = "An error occurred. Please check the console for details.";
    
                try {
                    // Attempt to parse the response as JSON
                    const response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        errorMessage = response.error; // Use the error message from the server
                    } else if (response.msg) {
                        errorMessage = response.msg; // Use the message from the server
                    }
                } catch (e) {
                    // If parsing fails, use the raw response text or a generic message
                    errorMessage = xhr.responseText || "An unexpected error occurred. Please try again.";
                }
    
                // Log the error to the console
                console.error("Error:", errorMessage);
    
                // Display a user-friendly alert
                alert(errorMessage);
            }
        });
    }

    // Handle form submission
    $("#chat-form").submit(function (e) {
        e.preventDefault(); // Prevent the default form submission
        sendQuery(); // Send the query to the chatbot
    });

    // Handle Enter key press in the input field
    $("#question").keypress(function (e) {
        if (e.which === 13) { // 13 is the keycode for the Enter key
            e.preventDefault(); // Prevent the default form submission
            sendQuery(); // Send the query to the chatbot
        }
    });
});