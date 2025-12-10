const API_URL = `${window.location.origin}/api/users`;

let users = [];
let userModal;

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    const modalElement = document.getElementById('userModal');
    if (modalElement) {
        userModal = new bootstrap.Modal(modalElement);
    }

    setupForm();
    loadUsers();
});

// Настраиваем обработчик формы добавления пользователя
function setupForm() {
    const form = document.getElementById('addUserForm');
    if (!form) return;

    form.addEventListener('submit', handleAddUser);
}

// Загрузка списка пользователей с сервера
async function loadUsers() {
    const spinner = document.getElementById('loadingSpinner');
    const tableWrapper = document.getElementById('usersTableWrapper');
    const meta = document.getElementById('usersMeta');
    const emptyState = document.getElementById('emptyState');

    spinner.classList.remove('d-none');
    tableWrapper.classList.add('d-none');
    emptyState.classList.add('d-none');

    try {
        const res = await fetch(`${API_URL}?page=1&per_page=100`);
        const json = await res.json();

        if (!res.ok || !json.success) {
            throw new Error(json.error || `HTTP ${res.status}`);
        }

        users = json.data || [];
        renderUsersTable(users);

        if (json.metadata && typeof json.metadata.total === 'number') {
            meta.textContent = `${json.metadata.total} пользователь(ей)`;
        } else {
            meta.textContent = `${users.length} пользователь(ей)`;
        }

        if (!users.length) {
            emptyState.classList.remove('d-none');
        }

        spinner.classList.add('d-none');
        tableWrapper.classList.remove('d-none');
    } catch (e) {
        console.error(e);
        spinner.classList.add('d-none');
        showMessage('Не удалось загрузить пользователей. Попробуйте ещё раз.', 'danger');
    }
}

// Рендер таблицы пользователей
function renderUsersTable(list) {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!list.length) {
        return;
    }

    for (const user of list) {
        const tr = document.createElement('tr');

        tr.innerHTML = `
      <td>${user.id}</td>
      <td>${escapeHtml(user.name)}</td>
      <td>${escapeHtml(user.email)}</td>
      <td class="text-end">
        <button class="btn btn-outline-primary btn-sm me-1 btn-view-user" data-user-id="${user.id}">
          Просмотр
        </button>
        <button class="btn btn-outline-danger btn-sm" data-user-id="${user.id}">
          Удалить
        </button>
      </td>
    `;

        const [viewBtn, deleteBtn] = tr.querySelectorAll('button');

        viewBtn.addEventListener('click', () => openUserModal(user.id));
        deleteBtn.addEventListener('click', () => deleteUser(user.id));

        tbody.appendChild(tr);
    }
}

// Обработчик отправки формы добавления пользователя
async function handleAddUser(event) {
    event.preventDefault();

    const nameInput = document.getElementById('nameInput');
    const emailInput = document.getElementById('emailInput');

    const payload = {
        name: nameInput.value.trim(),
        email: emailInput.value.trim()
    };

    if (!payload.name || !payload.email) {
        showMessage('Имя и email обязательны.', 'warning');
        return;
    }

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const json = await res.json();

        if (!res.ok || !json.success) {
            const details = json.details ? JSON.stringify(json.details) : '';
            throw new Error(json.error || details || 'Ошибка создания пользователя');
        }

        showMessage('Пользователь успешно создан.', 'success');

        // Обновляем список
        await loadUsers();
        event.target.reset();
    } catch (e) {
        console.error(e);
        showMessage(e.message, 'danger');
    }
}

// Открыть модальное окно с инфой о пользователе
async function openUserModal(userId) {
    try {
        const res = await fetch(`${API_URL}/${userId}`);
        const json = await res.json();

        if (!res.ok || !json.success) {
            throw new Error(json.error || `HTTP ${res.status}`);
        }

        const user = json.data;
        fillUserModal(user);
        if (userModal) {
            userModal.show();
        }
    } catch (e) {
        console.error(e);
        showMessage('Не удалось загрузить пользователя.', 'danger');
    }
}

function fillUserModal(user) {
    document.getElementById('userDetailId').textContent = user.id;
    document.getElementById('userDetailName').textContent = user.name;
    document.getElementById('userDetailEmail').textContent = user.email;
    document.getElementById('userDetailCreatedAt').textContent = formatDate(user.created_at);
    document.getElementById('userDetailUpdatedAt').textContent = formatDate(user.updated_at);
    document.getElementById('userDetailIsActive').textContent = user.is_active ? 'Да' : 'Нет';
}

// Удалить пользователя
async function deleteUser(userId) {
    if (!confirm(`Удалить пользователя #${userId}?`)) {
        return;
    }

    try {
        const res = await fetch(`${API_URL}/${userId}?soft=true`, {
            method: 'DELETE'
        });
        const json = await res.json();

        if (!res.ok || !json.success) {
            throw new Error(json.error || `HTTP ${res.status}`);
        }

        showMessage('Пользователь удалён.', 'success');
        await loadUsers();
    } catch (e) {
        console.error(e);
        showMessage('Не удалось удалить пользователя.', 'danger');
    }
}

// Вспомогательные функции

function showMessage(message, type = 'info', timeout = 4000) {
    const placeholder = document.getElementById('alertPlaceholder');
    if (!placeholder) return;

    const wrapper = document.createElement('div');
    wrapper.className = `alert alert-${type}`;
    wrapper.role = 'alert';
    wrapper.textContent = message;

    placeholder.appendChild(wrapper);

    setTimeout(() => {
        wrapper.remove();
    }, timeout);
}

function formatDate(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return isoString;
    return date.toLocaleString();
}

function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
