const API_URL = 'http://127.0.0.1:5000';
let users = [];

const userModal = new bootstrap.Modal(document.getElementById('userModal'));

document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    setupForm();
});

function setupForm() {
    const form = document.getElementById('addUserForm');
    form.addEventListener('submit', handleAddUser);
}

async function loadUsers() {
    const spinner = document.getElementById('loadingSpinner');
    const tableWrapper = document.getElementById('usersTableWrapper');
    const meta = document.getElementById('usersMeta');

    spinner.classList.remove('d-none');
    tableWrapper.classList.add('d-none');

    try {
        const res = await fetch(`${API_URL}/users`);
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        users = await res.json();

        renderUsersTable(users);
        meta.textContent = `${users.length} user${users.length === 1 ? '' : 's'}`;
        spinner.classList.add('d-none');
        tableWrapper.classList.remove('d-none');
    } catch (e) {
        spinner.classList.add('d-none');
        showMessage('Failed to load users. Please try again.', 'danger');
        console.error(e);
    }
}

function renderUsersTable(list) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';

    if (!list.length) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" class="text-center text-muted py-4 small">
              No users found.
            </td>
          </tr>`;
        return;
    }

    list.forEach((user) => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
          <td>${user.id}</td>
          <td>${escapeHtml(user.name)}</td>
          <td>${escapeHtml(user.email)}</td>
          <td class="text-end">
            <button type="button" class="btn btn-outline-secondary btn-view-user" data-user-id="${user.id}">
              View
            </button>
          </td>
        `;

        const viewButton = tr.querySelector('[data-user-id]');
        viewButton.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = Number(viewButton.getAttribute('data-user-id'));
            if (id) openUserModal(id);
        });

        tbody.appendChild(tr);
    });
}

async function openUserModal(userId) {
    const content = document.getElementById('userDetailsContent');
    content.innerHTML = `
        <div class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-secondary" role="status"></div>
        </div>
      `;
    userModal.show();

    try {
        const res = await fetch(`${API_URL}/users/${userId}`);
        if (!res.ok) {
            if (res.status === 404) {
                throw new Error('User not found');
            }
            throw new Error(`HTTP ${res.status}`);
        }
        const user = await res.json();

        content.innerHTML = `
          <div class="user-detail-row">
            <div class="user-detail-label">ID</div>
            <div class="user-detail-value">${user.id}</div>
          </div>
          <div class="user-detail-row">
            <div class="user-detail-label">Name</div>
            <div class="user-detail-value">${escapeHtml(user.name)}</div>
          </div>
          <div class="user-detail-row">
            <div class="user-detail-label">Email</div>
            <div class="user-detail-value">
              <a href="mailto:${escapeHtml(user.email)}" class="link-body-emphasis">
                ${escapeHtml(user.email)}
              </a>
            </div>
          </div>
        `;
    } catch (e) {
        content.innerHTML = `
          <div class="alert alert-danger mb-0">
            ${e.message || 'Failed to load user.'}
          </div>
        `;
    }
}

async function handleAddUser(event) {
    event.preventDefault();

    const nameInput = document.getElementById('userName');
    const emailInput = document.getElementById('userEmail');
    const button = event.target.querySelector('button[type="submit"]');

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();

    if (!name || !email) {
        showMessage('Fill in all fields.', 'warning');
        return;
    }

    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = 'Saving...';

    try {
        const res = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email }),
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || 'Failed to create user.');
        }

        showMessage('User created successfully.', 'success');
        nameInput.value = '';
        emailInput.value = '';

        await loadUsers();
    } catch (e) {
        showMessage(e.message, 'danger');
        console.error(e);
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('messageContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} d-flex justify-content-between align-items-center`;
    alert.innerHTML = `
        <span>${message}</span>
        <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
    container.appendChild(alert);

    setTimeout(() => {
        alert.classList.add('fade');
        setTimeout(() => alert.remove(), 200);
    }, 4000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text ?? '';
    return div.innerHTML;
}
