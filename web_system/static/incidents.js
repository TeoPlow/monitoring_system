const loginForm = document.getElementById('login-form');
const logoutBtn = document.getElementById('logout-btn');
const incidentsContainer = document.getElementById('incidents-container');
const incidentsTableBody = document.querySelector('#incidents-table tbody');
const errorDiv = document.getElementById('error');

function showError(msg) {
    errorDiv.textContent = msg;
}

function clearError() {
    errorDiv.textContent = '';
}

function showIncidents(incidents) {
    incidentsTableBody.innerHTML = '';
    incidents.forEach(inc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${inc.incident_type}</td>
            <td>${inc.server_name}</td>
            <td>${inc.cpu}</td>
            <td>${inc.mem}</td>
            <td>${inc.disk}</td>
            <td>${inc.uptime}</td>
            <td>${inc.checked_at}</td>
        `;
        incidentsTableBody.appendChild(row);
    });
}

function fetchIncidents() {
    fetch('/web_system/api/incidents/', { credentials: 'include' })
        .then(res => {
            if (res.status === 401) throw new Error('Требуется вход');
            return res.json();
        })
        .then(data => {
            showIncidents(data.incidents);
            incidentsContainer.style.display = '';
            logoutBtn.style.display = '';
            loginForm.style.display = 'none';
            clearError();
        })
        .catch(err => {
            incidentsContainer.style.display = 'none';
            logoutBtn.style.display = 'none';
            loginForm.style.display = '';
            showError(err.message);
        });
}

loginForm.onsubmit = function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch('/web_system/api/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
    })
    .then(res => {
        if (!res.ok) throw new Error('Неверный логин или пароль');
        return res.json();
    })
    .then(() => {
        fetchIncidents();
    })
    .catch(err => {
        showError(err.message);
    });
};

logoutBtn.onclick = function() {
    fetch('/web_system/api/logout/', { credentials: 'include' })
        .then(() => {
            incidentsContainer.style.display = 'none';
            logoutBtn.style.display = 'none';
            loginForm.style.display = '';
        });
};

setInterval(() => {
    if (incidentsContainer.style.display !== 'none') {
        fetchIncidents();
    }
}, 5000);

fetchIncidents();
