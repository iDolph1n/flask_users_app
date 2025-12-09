const API_URL = 'http://localhost:5000';

let usersData = [];
const userModal = new bootstrap.Modal(document.getElementById('userModal'));

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    setupEventListeners();
});

// Настройка обработчиков событий
function setupEventListeners() {
    // Форма добавления пользователя
    document.getElementById('addUserForm').addEventListener('submit', handleAddUser);
}

async function loadUsers() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const usersTable = document.getElementById('usersTable');

    try {
        loadingSpinner.classList.remove('d-none');
        usersTable.classList.add('d-none');

        const response = await fetch(`${API_URL}/users`);

        if (!response.ok) {
            throw new Error(`Ошибка загрузки: ${response.status}`);
        }

        usersData = await response.json();
        displayUsers(usersData);

        loadingSpinner.classList.add('d-none');
        usersTable.classList.remove('d-none');

    } catch (error) {
        loadingSpinner.classList.add('d-none');
        showMessage('Ошибка загрузки пользователей: ' + error.message, 'danger');
        console.error('Ошибка:', error);
    }
}

// Отображение пользователей в таблице
function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';

    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted">
                    Пользователи не найдены
                </td>
            </tr>
        `;
        return;
    }

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${escapeHtml(user.name)}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="showUserDetails(${user.id})">
                    Подробнее
                </button>
            </td>
        `;

        // Клик по строке тоже показывает детали
        row.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                showUserDetails(user.id);
            }
        });

        tbody.appendChild(row);
    });
}

async function showUserDetails(userId) {
    const modalContent = document.getElementById('userDetailsContent');

    try {
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;

        userModal.show();

        const response = await fetch(`${API_URL}/users/${userId}`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Пользователь не найден');
            }
            throw new Error(`Ошибка: ${response.status}`);
        }

        const user = await response.json();

        modalContent.innerHTML = `
            <div class="user-detail-item">
                <div class="user-detail-label">🆔 ID:</div>
                <div>${user.id}</div>
            </div>
            <div class="user-detail-item">
                <div class="user-detail-label">👤 Имя:</div>
                <div>${escapeHtml(user.name)}</div>
            </div>
            <div class="user-detail-item">
                <div class="user-detail-label">📧 Email:</div>
                <div><a href="mailto:${user.email}">${escapeHtml(user.email)}</a></div>
            </div>
        `;

    } catch (error) {
        modalContent.innerHTML = `
            <div class="alert alert-danger">
                ${error.message}
            </div>
        `;
        console.error('Ошибка:', error);
    }
}

async function handleAddUser(e) {
    e.preventDefault();

    const nameInput = document.getElementById('userName');
    const emailInput = document.getElementById('userEmail');
    const submitButton = e.target.querySelector('button[type="submit"]');

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();

    if (!name || !email) {
        showMessage('Заполните все поля', 'warning');
        return;
    }

    try {
        // Блокировать кнопку
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Добавление...';

        const response = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('✅ Пользователь успешно добавлен!', 'success');

            // Очистить форму
            nameInput.value = '';
            emailInput.value = '';

            // Обновить список без перезагрузки страницы
            await loadUsers();

        } else {
            showMessage('❌ ' + (data.error || 'Ошибка добавления пользователя'), 'danger');
        }

    } catch (error) {
        showMessage('❌ Ошибка соединения: ' + error.message, 'danger');
        console.error('Ошибка:', error);
    } finally {
        // Разблокировка кнопки
        submitButton.disabled = false;
        submitButton.innerHTML = 'Добавить';
    }
}

// Показать сообщение (успех/ошибка)
function showMessage(message, type) {
    const container = document.getElementById('messageContainer');

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(alert);

    // Автоматически убираем через 5 секунд
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Защита от XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
