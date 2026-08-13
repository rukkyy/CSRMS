// CSRMS Authentication Handler

document.addEventListener("DOMContentLoaded", () => {
    // Determine page context
    const path = window.location.pathname;
    
    // Redirect logic: If logged in, skip login/register
    if (isAuthenticated()) {
        if (path === "/login" || path === "/register" || path === "/") {
            window.location.href = "/dashboard";
            return;
        }
    } else {
        // If not logged in, force authentication pages
        if (path !== "/login" && path !== "/register" && path !== "/") {
            window.location.href = "/login";
            return;
        }
    }

    // Set up form submission event listeners
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }

    // Set up logout button if present
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Load active user details into top navigation bar if available
    const navUser = document.getElementById("nav-user-name");
    const navRole = document.getElementById("nav-user-role");
    if (navUser && navRole) {
        const user = getCurrentUser();
        if (user) {
            navUser.textContent = user.name;
            navRole.textContent = user.role;
        }
    }
});

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const alertEl = document.getElementById("alert-msg");

    if (alertEl) {
        alertEl.style.display = "none";
        alertEl.className = "alert";
    }

    try {
        const response = await apiFetch("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password })
        });

        // Store session tokens and metadata
        localStorage.setItem("csrms_token", response.access_token);
        localStorage.setItem("csrms_user", JSON.stringify({
            name: response.name,
            email: response.email,
            role: response.role
        }));

        // Redirect to dashboard
        window.location.href = "/dashboard";
    } catch (err) {
        if (alertEl) {
            alertEl.textContent = err.message || "Failed to authenticate";
            alertEl.classList.add("alert-danger");
        }
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const alertEl = document.getElementById("alert-msg");

    if (alertEl) {
        alertEl.style.display = "none";
        alertEl.className = "alert";
    }

    // Confirm passwords match
    if (password !== confirmPassword) {
        if (alertEl) {
            alertEl.textContent = "Passwords do not match";
            alertEl.classList.add("alert-danger");
        }
        return;
    }

    try {
        await apiFetch("/api/auth/register", {
            method: "POST",
            body: JSON.stringify({
                name,
                email,
                password,
                role: "REQUESTER" // Default role
            })
        });

        // Registration successful: Alert and redirect to login
        if (alertEl) {
            alertEl.textContent = "Registration successful! Redirecting to login...";
            alertEl.classList.add("alert-success");
        }

        setTimeout(() => {
            window.location.href = "/login";
        }, 1500);
    } catch (err) {
        if (alertEl) {
            alertEl.textContent = err.message || "Registration failed";
            alertEl.classList.add("alert-danger");
        }
    }
}
