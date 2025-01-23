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
            localStorage.setItem("jwt_token", result.access_token);
            window.location.href = '/';
        } else {
            const result = await response.json();
            alert(result.error || 'Login failed');
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred. Please try again later.');
    }
}

$(document).ready(function () {
    $('#login-form').submit(handleLogin);
});
