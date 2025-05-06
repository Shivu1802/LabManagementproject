// Handle login form submission with backend integration

document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const role = document.getElementById('role').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password, role })
        });
        const result = await response.json();
        if (result.success) {
            alert(result.message);
            // Store username and role in localStorage
            localStorage.setItem('username', username);
            localStorage.setItem('role', role);
            // Redirect to dashboard or home page based on role
            if (role === 'admin') {
                window.location.href = 'admin_dashboard.html';
            } else {
                window.location.href = 'student_dashboard.html';
            }
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Error connecting to server.');
    }
});
