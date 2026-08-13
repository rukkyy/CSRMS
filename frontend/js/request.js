// CSRMS Service Request Creation & Details Manager

document.addEventListener("DOMContentLoaded", () => {
    if (!isAuthenticated()) return;

    const user = getCurrentUser();
    const path = window.location.pathname;

    // 1. Create Page Init
    if (path === "/request/create") {
        loadCategoriesSelect();
        const createForm = document.getElementById("create-request-form");
        if (createForm) {
            createForm.addEventListener("submit", handleCreateRequest);
        }
    }

    // 2. Details Page Init
    if (path === "/request/details") {
        const urlParams = new URLSearchParams(window.location.search);
        const requestId = urlParams.get("id");
        if (requestId) {
            loadRequestDetails(requestId, user);
        } else {
            window.location.href = "/dashboard";
        }
    }
});

/**
 * Fetch and load category choices for the create request form dropdown.
 */
async function loadCategoriesSelect() {
    try {
        const categories = await apiFetch("/api/requests/categories");
        const selectEl = document.getElementById("category_id");
        if (selectEl) {
            selectEl.innerHTML = '<option value="">-- Select Category --</option>' + 
                categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
        }
    } catch (err) {
        console.error("Failed to load categories:", err);
    }
}

/**
 * Handle new request submission.
 */
async function handleCreateRequest(e) {
    e.preventDefault();
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const location = document.getElementById("location").value;
    const category_id = parseInt(document.getElementById("category_id").value);
    const priority = document.getElementById("priority").value;
    const alertEl = document.getElementById("alert-msg");

    if (alertEl) {
        alertEl.style.display = "none";
        alertEl.className = "alert";
    }

    try {
        await apiFetch("/api/requests/", {
            method: "POST",
            body: JSON.stringify({ title, description, location, category_id, priority })
        });

        if (alertEl) {
            alertEl.textContent = "Service request submitted successfully! Redirecting...";
            alertEl.classList.add("alert-success");
        }

        setTimeout(() => {
            window.location.href = "/dashboard";
        }, 1500);

    } catch (err) {
        if (alertEl) {
            alertEl.textContent = err.message || "Failed to submit request";
            alertEl.classList.add("alert-danger");
        }
    }
}

/**
 * Load request details and dynamically render control panels based on user role.
 */
async function loadRequestDetails(requestId, user) {
    try {
        const req = await apiFetch(`/api/requests/${requestId}`);
        
        // Populate standard details fields
        document.getElementById("detail-id").textContent = `#${req.id}`;
        document.getElementById("detail-title").textContent = req.title;
        document.getElementById("detail-status").innerHTML = `<span class="badge badge-${req.status.toLowerCase().replace("_", "-")}">${req.status.replace("_", " ")}</span>`;
        document.getElementById("detail-priority").innerHTML = `<span class="badge badge-${req.priority.toLowerCase()}">${req.priority}</span>`;
        document.getElementById("detail-category").textContent = req.category.name;
        document.getElementById("detail-location").textContent = req.location;
        document.getElementById("detail-requester").textContent = req.requester.name;
        document.getElementById("detail-assignee").textContent = req.assignee ? req.assignee.name : "Unassigned";
        document.getElementById("detail-created").textContent = new Date(req.created_at).toLocaleString();
        document.getElementById("detail-updated").textContent = new Date(req.updated_at).toLocaleString();
        document.getElementById("detail-description").textContent = req.description;

        // Render resolution notes if available
        const resolutionBox = document.getElementById("detail-resolution-box");
        if (req.resolution_notes) {
            resolutionBox.style.display = "block";
            document.getElementById("detail-resolution").textContent = req.resolution_notes;
        } else {
            resolutionBox.style.display = "none";
        }

        // Render actions control panel
        renderControlPanel(req, user);

    } catch (err) {
        console.error("Failed to load details:", err);
        alert("Error loading request details: " + err.message);
        window.location.href = "/dashboard";
    }
}

/**
 * Renders the sidebar actions dashboard panel based on permissions.
 */
async function renderControlPanel(req, user) {
    const panel = document.getElementById("management-panel-content");
    if (!panel) return;

    panel.innerHTML = ""; // Clear existing

    // 1. REQUESTER WORKFLOW
    if (user.role === "REQUESTER") {
        if (req.status === "RESOLVED") {
            panel.innerHTML = `
                <p style="margin-bottom:1rem; font-size:0.875rem; color:var(--text-secondary);">
                    Maintenance staff has resolved this issue. Please verify and close.
                </p>
                <button class="btn btn-primary" id="btn-close-ticket">Close Request</button>
            `;
            document.getElementById("btn-close-ticket").addEventListener("click", () => transitionStatus(req.id, "CLOSED"));
        } else if (req.status === "SUBMITTED") {
            panel.innerHTML = `
                <p style="margin-bottom:1rem; font-size:0.875rem; color:var(--text-secondary);">
                    This request is submitted and pending review. You can modify details below if needed.
                </p>
                <button class="btn btn-secondary" id="btn-edit-toggle">Edit Details</button>
                <div id="requester-edit-form" style="display:none; margin-top:1rem;">
                    <div class="form-group">
                        <label for="edit-title">Title</label>
                        <input type="text" id="edit-title" class="form-control" value="${escapeHtml(req.title)}">
                    </div>
                    <div class="form-group">
                        <label for="edit-location">Location</label>
                        <input type="text" id="edit-location" class="form-control" value="${escapeHtml(req.location)}">
                    </div>
                    <div class="form-group">
                        <label for="edit-desc">Description</label>
                        <textarea id="edit-desc" class="form-control" rows="4">${escapeHtml(req.description)}</textarea>
                    </div>
                    <button class="btn btn-primary" id="btn-save-edit" style="margin-top:0.5rem;">Save Changes</button>
                </div>
            `;
            
            const editToggle = document.getElementById("btn-edit-toggle");
            const editForm = document.getElementById("requester-edit-form");
            editToggle.addEventListener("click", () => {
                if (editForm.style.display === "none") {
                    editForm.style.display = "block";
                    editToggle.textContent = "Cancel";
                } else {
                    editForm.style.display = "none";
                    editToggle.textContent = "Edit Details";
                }
            });

            document.getElementById("btn-save-edit").addEventListener("click", () => saveRequesterEdits(req.id));
        } else {
            panel.innerHTML = `<p style="font-size:0.875rem; color:var(--text-muted);">This request is currently ${req.status} and cannot be modified.</p>`;
        }
    }

    // 2. MAINTENANCE WORKFLOW
    else if (user.role === "MAINTENANCE") {
        if (req.status === "ASSIGNED") {
            panel.innerHTML = `
                <p style="margin-bottom:1rem; font-size:0.875rem; color:var(--text-secondary);">
                    Start progress on this request when you begin working on it.
                </p>
                <button class="btn btn-primary" id="btn-start-work">Start Work</button>
            `;
            document.getElementById("btn-start-work").addEventListener("click", () => transitionStatus(req.id, "IN_PROGRESS"));
        } else if (req.status === "IN_PROGRESS") {
            panel.innerHTML = `
                <div class="form-group">
                    <label for="resolution-notes">Resolution Notes</label>
                    <textarea id="resolution-notes" class="form-control" rows="4" placeholder="Describe how the problem was resolved (min. 5 chars)..."></textarea>
                </div>
                <div id="error-notes" class="alert alert-danger" style="margin-top:0.5rem; display:none;"></div>
                <button class="btn btn-primary" id="btn-resolve-work" style="margin-top:0.5rem;">Resolve Issue</button>
            `;
            document.getElementById("btn-resolve-work").addEventListener("click", () => resolveRequest(req.id));
        } else {
            panel.innerHTML = `<p style="font-size:0.875rem; color:var(--text-muted);">Request is in state: ${req.status}. No operations available.</p>`;
        }
    }

    // 3. ADMIN WORKFLOW
    else if (user.role === "ADMIN") {
        try {
            // Load staff list for assignment dropdown
            const staffList = await apiFetch("/api/admin/users?role=MAINTENANCE");
            const staffOptions = staffList.map(s => 
                `<option value="${s.id}" ${req.assigned_to === s.id ? "selected" : ""}>${s.name}</option>`
            ).join("");

            panel.innerHTML = `
                <div class="form-group">
                    <label for="admin-assignee">Assign Staff</label>
                    <select id="admin-assignee" class="form-control">
                        <option value="0">Unassigned</option>
                        ${staffOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label for="admin-priority">Change Priority</label>
                    <select id="admin-priority" class="form-control">
                        <option value="LOW" ${req.priority === "LOW" ? "selected" : ""}>LOW</option>
                        <option value="MEDIUM" ${req.priority === "MEDIUM" ? "selected" : ""}>MEDIUM</option>
                        <option value="HIGH" ${req.priority === "HIGH" ? "selected" : ""}>HIGH</option>
                        <option value="URGENT" ${req.priority === "URGENT" ? "selected" : ""}>URGENT</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="admin-status">Change Status</label>
                    <select id="admin-status" class="form-control">
                        <option value="SUBMITTED" ${req.status === "SUBMITTED" ? "selected" : ""}>SUBMITTED</option>
                        <option value="ASSIGNED" ${req.status === "ASSIGNED" ? "selected" : ""}>ASSIGNED</option>
                        <option value="IN_PROGRESS" ${req.status === "IN_PROGRESS" ? "selected" : ""}>IN PROGRESS</option>
                        <option value="RESOLVED" ${req.status === "RESOLVED" ? "selected" : ""}>RESOLVED</option>
                        <option value="CLOSED" ${req.status === "CLOSED" ? "selected" : ""}>CLOSED</option>
                    </select>
                </div>
                <div class="form-group" id="admin-notes-group" style="display: ${req.status === "RESOLVED" ? "block" : "none"};">
                    <label for="admin-resolution-notes">Resolution Notes</label>
                    <textarea id="admin-resolution-notes" class="form-control" rows="3">${escapeHtml(req.resolution_notes || "")}</textarea>
                </div>
                <div id="admin-error" class="alert alert-danger" style="margin-top:0.5rem; display:none;"></div>
                <button class="btn btn-primary" id="btn-admin-save" style="margin-top:0.5rem; width:100%;">Save Changes</button>
            `;

            // Toggle admin notes visible based on chosen status
            document.getElementById("admin-status").addEventListener("change", (e) => {
                const group = document.getElementById("admin-notes-group");
                if (e.target.value === "RESOLVED") {
                    group.style.display = "block";
                } else {
                    group.style.display = "none";
                }
            });

            document.getElementById("btn-admin-save").addEventListener("click", () => saveAdminUpdates(req.id));

        } catch (err) {
            panel.innerHTML = `<p style="color:var(--danger);">Error initializing settings: ${err.message}</p>`;
        }
    }
}

/**
 * Handle state transitions.
 */
async function transitionStatus(requestId, nextStatus) {
    try {
        await apiFetch(`/api/requests/${requestId}`, {
            method: "PUT",
            body: JSON.stringify({ status: nextStatus })
        });
        window.location.reload();
    } catch (err) {
        alert("Operation failed: " + err.message);
    }
}

/**
 * Handle requester save edits.
 */
async function saveRequesterEdits(requestId) {
    const title = document.getElementById("edit-title").value;
    const location = document.getElementById("edit-location").value;
    const description = document.getElementById("edit-desc").value;

    try {
        await apiFetch(`/api/requests/${requestId}`, {
            method: "PUT",
            body: JSON.stringify({ title, location, description })
        });
        window.location.reload();
    } catch (err) {
        alert("Failed to save changes: " + err.message);
    }
}

/**
 * Handle maintenance resolve submission.
 */
async function resolveRequest(requestId) {
    const notes = document.getElementById("resolution-notes").value;
    const errEl = document.getElementById("error-notes");

    if (errEl) {
        errEl.style.display = "none";
    }

    if (!notes || notes.trim().length < 5) {
        if (errEl) {
            errEl.textContent = "Resolution notes must be at least 5 characters.";
            errEl.style.display = "block";
        }
        return;
    }

    try {
        await apiFetch(`/api/requests/${requestId}`, {
            method: "PUT",
            body: JSON.stringify({
                status: "RESOLVED",
                resolution_notes: notes
            })
        });
        window.location.reload();
    } catch (err) {
        if (errEl) {
            errEl.textContent = err.message || "Failed to resolve request.";
            errEl.style.display = "block";
        }
    }
}

/**
 * Handle admin configuration updates save.
 */
async function saveAdminUpdates(requestId) {
    const assignedVal = parseInt(document.getElementById("admin-assignee").value);
    const priority = document.getElementById("admin-priority").value;
    const statusVal = document.getElementById("admin-status").value;
    const notes = document.getElementById("admin-resolution-notes") ? document.getElementById("admin-resolution-notes").value : "";
    const errEl = document.getElementById("admin-error");

    if (errEl) {
        errEl.style.display = "none";
    }

    const payload = {
        priority,
        status: statusVal,
        assigned_to: assignedVal
    };

    if (statusVal === "RESOLVED") {
        if (!notes || notes.trim().length < 5) {
            if (errEl) {
                errEl.textContent = "Resolution notes are required when setting status to RESOLVED.";
                errEl.style.display = "block";
            }
            return;
        }
        payload.resolution_notes = notes;
    }

    try {
        await apiFetch(`/api/requests/${requestId}`, {
            method: "PUT",
            body: JSON.stringify(payload)
        });
        window.location.reload();
    } catch (err) {
        if (errEl) {
            errEl.textContent = err.message || "Failed to update request.";
            errEl.style.display = "block";
        }
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}
