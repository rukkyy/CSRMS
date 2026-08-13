// CSRMS Dashboard Manager

document.addEventListener("DOMContentLoaded", () => {
    if (!isAuthenticated()) return;

    const user = getCurrentUser();
    
    // Customize UI view depending on role
    initRoleView(user.role);

    // Initial data load
    loadDashboardData(user.role);

    // Register filters listener
    const statusFilter = document.getElementById("filter-status");
    const priorityFilter = document.getElementById("filter-priority");

    if (statusFilter) {
        statusFilter.addEventListener("change", () => loadDashboardData(user.role));
    }
    if (priorityFilter) {
        priorityFilter.addEventListener("change", () => loadDashboardData(user.role));
    }
});

function initRoleView(role) {
    // Show role-specific dashboard panels
    const adminStats = document.getElementById("admin-stats");
    const staffStats = document.getElementById("staff-stats");
    const requesterStats = document.getElementById("requester-stats");
    const createReqBtn = document.getElementById("btn-create-request");

    // Hide all first
    if (adminStats) adminStats.style.display = "none";
    if (staffStats) staffStats.style.display = "none";
    if (requesterStats) requesterStats.style.display = "none";
    if (createReqBtn) createReqBtn.style.display = "none";

    // Unhide corresponding panel
    if (role === "ADMIN") {
        if (adminStats) adminStats.style.display = "grid";
    } else if (role === "MAINTENANCE") {
        if (staffStats) staffStats.style.display = "grid";
    } else { // REQUESTER
        if (requesterStats) requesterStats.style.display = "grid";
        if (createReqBtn) createReqBtn.style.display = "inline-flex";
    }
}

async function loadDashboardData(role) {
    try {
        // 1. Fetch Stats
        if (role === "ADMIN") {
            const stats = await apiFetch("/api/admin/dashboard/stats");
            document.getElementById("admin-total-reqs").textContent = stats.total_requests;
            document.getElementById("admin-submitted").textContent = stats.status_counts.SUBMITTED;
            document.getElementById("admin-assigned").textContent = stats.status_counts.ASSIGNED;
            document.getElementById("admin-inprogress").textContent = stats.status_counts.IN_PROGRESS;
            document.getElementById("admin-resolved").textContent = stats.status_counts.RESOLVED;
        } else if (role === "MAINTENANCE") {
            const stats = await apiFetch("/api/maintenance/dashboard/stats");
            document.getElementById("staff-total-assigned").textContent = stats.total_assigned;
            document.getElementById("staff-pending").textContent = stats.status_counts.ASSIGNED;
            document.getElementById("staff-inprogress").textContent = stats.status_counts.IN_PROGRESS;
            document.getElementById("staff-resolved").textContent = stats.status_counts.RESOLVED;
        }

        // 2. Fetch & Render Request Table
        const statusVal = document.getElementById("filter-status").value;
        const priorityVal = document.getElementById("filter-priority").value;

        let queryParams = [];
        if (statusVal) queryParams.push(`status=${statusVal}`);
        if (priorityVal) queryParams.push(`priority=${priorityVal}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join("&")}` : "";
        const requests = await apiFetch(`/api/requests${queryString}`);

        // Update Requester Stats client-side based on returned data
        if (role === "REQUESTER") {
            const total = requests.length;
            const pending = requests.filter(r => r.status !== "RESOLVED" && r.status !== "CLOSED").length;
            const resolved = requests.filter(r => r.status === "RESOLVED").length;
            document.getElementById("req-total").textContent = total;
            document.getElementById("req-pending").textContent = pending;
            document.getElementById("req-resolved").textContent = resolved;
        }

        renderRequestsTable(requests, role);

    } catch (err) {
        console.error("Dashboard error:", err);
        const tableBody = document.getElementById("requests-table-body");
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="7" class="empty-state"><span class="badge badge-urgent">Error loading records: ${err.message}</span></td></tr>`;
        }
    }
}

function renderRequestsTable(requests, role) {
    const tableBody = document.getElementById("requests-table-body");
    if (!tableBody) return;

    if (requests.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <h3>No service requests found</h3>
                    <p>There are no requests matching the current filters.</p>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = requests.map(req => {
        const formattedDate = new Date(req.created_at).toLocaleDateString(undefined, {
            year: "numeric", month: "short", day: "numeric"
        });

        // Determine assignee name
        let assigneeName = "Unassigned";
        if (req.assignee) {
            assigneeName = req.assignee.name;
        }

        // Determine requester name (for admin view)
        const requesterInfoStr = role === "ADMIN" ? `<td>${req.requester.name}</td>` : "";

        return `
            <tr>
                <td><strong>#${req.id}</strong></td>
                <td><a href="/request/details?id=${req.id}" style="color: var(--accent-color); font-weight:600; text-decoration:none;">${escapeHtml(req.title)}</a></td>
                <td>${escapeHtml(req.category.name)}</td>
                ${requesterInfoStr}
                <td>${escapeHtml(req.location)}</td>
                <td><span class="badge badge-${req.priority.toLowerCase()}">${req.priority}</span></td>
                <td><span class="badge badge-${req.status.toLowerCase().replace("_", "-")}">${req.status.replace("_", " ")}</span></td>
                <td>${formattedDate}</td>
            </tr>
        `;
    }).join("");
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}
