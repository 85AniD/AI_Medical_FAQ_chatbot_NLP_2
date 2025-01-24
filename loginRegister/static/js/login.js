async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const result = await response.json();
            
            // Store the JWT token in localStorage
            localStorage.setItem("jwt_token", result.access_token);

            // Redirect based on user role
            if (result.role === 'user') {
                window.location.href = '/index'; // Redirect to user dashboard
            } else if (result.role === 'admin') {
                window.location.href = '/admin/dashboard'; // Redirect to admin dashboard
            } else {
                alert('Unknown role. Please contact support.');
            }
        } else {
            const result = await response.json();
            alert(result.error || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred. Please try again later.');
    }
}

$(document).ready(function () {
    $('#login-form').submit(handleLogin);
});