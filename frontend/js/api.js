// CSRMS Decoupled API Communication Client Wrapper

const API_BASE = window.location.origin;

/**
 * Perform an authenticated HTTP fetch request.
 * Automatically adds the Bearer Token from localStorage.
 */
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("csrms_token");
    
    // Set headers
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };
    
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    
    // Handle token expiration / unauthorized globally
    if (response.status === 401) {
        localStorage.removeItem("csrms_token");
        localStorage.removeItem("csrms_user");
        if (window.location.pathname !== "/login" && window.location.pathname !== "/register" && window.location.pathname !== "/") {
            window.location.href = "/login";
        }
        throw new Error("Session expired. Please log in again.");
    }
    
    // Parse response
    let data = null;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
        data = await response.json();
    }
    
    if (!response.ok) {
        const errorMessage = data && data.detail ? data.detail : "An error occurred";
        throw new Error(errorMessage);
    }
    
    return data;
}

/**
 * Check if the user is authenticated.
 */
function isAuthenticated() {
    return !!localStorage.getItem("csrms_token");
}

/**
 * Retrieve active user info.
 */
function getCurrentUser() {
    const userStr = localStorage.getItem("csrms_user");
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Log out and clear state.
 */
function logout() {
    localStorage.removeItem("csrms_token");
    localStorage.removeItem("csrms_user");
    window.location.href = "/login";
}
