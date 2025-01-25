function sendQuery() {
    const token = localStorage.getItem("jwt_token");
    if (!token) {
        alert("Authentication token is missing. Please log in again.");
        window.location.href = "/login";
        return;
    }

    const question = $("#question").val().trim();
    if (!question) {
        alert("Please enter a question.");
        return;
    }

    // Ensure the payload includes the `message` field
    const payload = { message: question };

        $.ajax({
            type: "POST",
            url: "/chatbot",
            contentType: "application/json",
            headers: {
                "Authorization": `Bearer ${token}`, // Include the token
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
            },
        });
    }

    function appendMessage(sender, message) {
        const messageHtml = `<p><strong>${sender}:</strong> ${message}</p>`;
        $("#response").append(messageHtml);
        $("#response").scrollTop($("#response")[0].scrollHeight);
    }

    function isTokenValid(token) {
        if (!token) return false; // No token present
        try {
            const payload = JSON.parse(atob(token.split(".")[1])); // Decode JWT
            const now = Math.floor(Date.now() / 1000); // Current timestamp
            return payload.exp > now; // Token is valid if not expired
        } catch (error) {
            console.error("Invalid token:", error);
            return false;
        }
    }

    if (!isTokenValid(localStorage.getItem("jwt_token"))) {
        alert("Your session has expired. Please log in again.");
        window.location.href = "/login";
    }

    $("#chat-form").submit(function (e) {
        e.preventDefault();
        sendQuery();
    });

    $("#question").keypress(function (e) {
        if (e.which === 13) {
            e.preventDefault();
            sendQuery();
        }
    });

