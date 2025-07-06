// Global state
let currentUser = null;
let authToken = null;
let currentView = 'dashboard';

// API Base URL
const API_BASE = '/api';

// DOM Elements
const loadingScreen = document.getElementById('loading-screen');
const loginScreen = document.getElementById('login-screen');
const appScreen = document.getElementById('app-screen');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// App initialization
async function initializeApp() {
    // Check for stored auth token
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    
    if (storedToken && storedUser) {
        authToken = storedToken;
        currentUser = JSON.parse(storedUser);
        
        // Verify token is still valid
        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                currentUser = data.user;
                showApp();
                return;
            }
        } catch (error) {
            console.error('Token verification failed:', error);
        }
        
        // Clear invalid token
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
    }
    
    // Show login screen
    setTimeout(() => {
        loadingScreen.classList.add('hidden');
        loginScreen.classList.remove('hidden');
    }, 1500);
}

// Event listeners setup
function setupEventListeners() {
    // Login form
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.dataset.view;
            if (view) {
                switchView(view);
            }
        });
    });
    
    // Logout
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Profile forms
    document.getElementById('profile-form').addEventListener('submit', handleProfileUpdate);
    document.getElementById('password-form').addEventListener('submit', handlePasswordChange);
    
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });
    
    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModals();
            }
        });
    });
    
    // Create buttons
    const createTaskBtn = document.getElementById('create-task-btn');
    if (createTaskBtn) {
        createTaskBtn.addEventListener('click', () => openTaskModal());
    }
    
    const createUserBtn = document.getElementById('create-user-btn');
    if (createUserBtn) {
        createUserBtn.addEventListener('click', () => openUserModal());
    }
    
    // Filters
    document.getElementById('status-filter').addEventListener('change', loadTasks);
}

// Authentication handlers
async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const credentials = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            
            // Store in localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showNotification('Login successful!', 'success');
            showApp();
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

async function handleRegister(e) {
    // Registration disabled - only admins can create users
    e.preventDefault();
    showNotification('Registration is disabled. Contact your administrator for account access.', 'error');
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    appScreen.classList.add('hidden');
    loginScreen.classList.remove('hidden');
    
    showNotification('Logged out successfully', 'info');
}

// App display
function showApp() {
    loadingScreen.classList.add('hidden');
    loginScreen.classList.add('hidden');
    appScreen.classList.remove('hidden');
    
    updateUserInfo();
    updateUIForRole();
    switchView('dashboard');
}

function updateUserInfo() {
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.display_name;
        document.getElementById('user-role').textContent = currentUser.role;
        
        // Update profile form
        document.getElementById('profile-display-name').value = currentUser.display_name;
        document.getElementById('profile-email').value = currentUser.email;
    }
}

function updateUIForRole() {
    const adminElements = document.querySelectorAll('.admin-only');
    const isAdmin = currentUser && (currentUser.role === 'admin' || currentUser.role === 'superadmin');
    
    adminElements.forEach(element => {
        if (isAdmin) {
            if (element.classList.contains('nav-link')) {
                element.classList.add('show-inline-flex');
            } else if (element.style.display === 'flex' || element.classList.contains('btn')) {
                element.classList.add('show-inline-flex');
            } else {
                element.classList.add('show');
            }
        } else {
            element.classList.remove('show', 'show-flex', 'show-inline-flex');
        }
    });
}

// View switching
function switchView(viewName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
    
    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    currentView = viewName;
    
    // Load view data
    switch (viewName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'tasks':
            loadTasks();
            break;
        case 'users':
            loadUsers();
            break;
        case 'profile':
            // Profile data already loaded
            break;
    }
}

// Dashboard
async function loadDashboard() {
    try {
        console.log('Loading dashboard with token:', authToken ? 'Token present' : 'No token');
        const [statsResponse, tasksResponse] = await Promise.all([
            fetch(`${API_BASE}/dashboard/stats`, {
                headers: { 
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            }),
            fetch(`${API_BASE}/tasks?limit=5`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            })
        ]);
        
        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            updateDashboardStats(statsData.stats);
        }
        
        if (tasksResponse.ok) {
            const tasksData = await tasksResponse.json();
            updateRecentTasks(tasksData.tasks.slice(0, 5));
        }
    } catch (error) {
        console.error('Dashboard load error:', error);
        showNotification('Failed to load dashboard data', 'error');
    }
}

function updateDashboardStats(stats) {
    document.getElementById('total-tasks').textContent = stats.total_tasks || stats.my_tasks || 0;
    document.getElementById('pending-tasks').textContent = stats.pending_tasks || 0;
    document.getElementById('in-progress-tasks').textContent = stats.in_progress_tasks || 0;
    document.getElementById('completed-tasks').textContent = stats.completed_tasks || 0;
}

function updateRecentTasks(tasks) {
    const container = document.getElementById('recent-tasks-list');
    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="text-muted">No recent tasks</p>';
        return;
    }
    
    tasks.forEach(task => {
        const taskElement = createTaskCard(task);
        container.appendChild(taskElement);
    });
}

// Tasks
async function loadTasks() {
    try {
        const statusFilter = document.getElementById('status-filter').value;
        const url = new URL(`${window.location.origin}${API_BASE}/tasks`);
        
        if (statusFilter) {
            url.searchParams.append('status', statusFilter);
        }
        
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateTasksList(data.tasks);
        } else {
            showNotification('Failed to load tasks', 'error');
        }
    } catch (error) {
        console.error('Tasks load error:', error);
        showNotification('Failed to load tasks', 'error');
    }
}

function updateTasksList(tasks) {
    const container = document.getElementById('tasks-list');
    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="text-muted">No tasks found</p>';
        return;
    }
    
    tasks.forEach(task => {
        const taskElement = createTaskCard(task);
        container.appendChild(taskElement);
    });
}

function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.onclick = () => openTaskModal(task);
    
    const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
    const assignee = task.assignee ? task.assignee.display_name : 'Unassigned';
    
    card.innerHTML = `
        <div class="task-header">
            <h4 class="task-title">${escapeHtml(task.title)}</h4>
            <span class="task-status ${task.status}">${task.status.replace('_', ' ')}</span>
        </div>
        <p class="task-description">${escapeHtml(task.description || '')}</p>
        <div class="task-meta">
            <div class="task-priority">
                <span class="priority-dot ${task.priority}"></span>
                <span>${task.priority}</span>
            </div>
            <span>Due: ${dueDate}</span>
            <span>Assigned to: ${assignee}</span>
        </div>
    `;
    
    return card;
}

// Users
async function loadUsers() {
    if (!currentUser || !['admin', 'superadmin'].includes(currentUser.role)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateUsersList(data.users);
        } else {
            showNotification('Failed to load users', 'error');
        }
    } catch (error) {
        console.error('Users load error:', error);
        showNotification('Failed to load users', 'error');
    }
}

function updateUsersList(users) {
    const container = document.getElementById('users-list');
    container.innerHTML = '';
    
    users.forEach(user => {
        const userElement = createUserCard(user);
        container.appendChild(userElement);
    });
}

function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';
    card.onclick = () => openUserModal(user);
    
    const initials = user.display_name.split(' ').map(n => n[0]).join('').toUpperCase();
    const joinDate = new Date(user.created_at).toLocaleDateString();
    
    card.innerHTML = `
        <div class="user-header">
            <div class="user-avatar">${initials}</div>
            <div class="user-info">
                <h4>${escapeHtml(user.display_name)}</h4>
                <span class="user-role-badge ${user.role}">${user.role}</span>
            </div>
        </div>
        <p><strong>Username:</strong> ${escapeHtml(user.username)}</p>
        <p><strong>Email:</strong> ${escapeHtml(user.email)}</p>
        <p><strong>Joined:</strong> ${joinDate}</p>
        <p><strong>Status:</strong> ${user.is_active ? 'Active' : 'Inactive'}</p>
    `;
    
    return card;
}

// Profile management
async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const profileData = {
        display_name: formData.get('display_name'),
        email: formData.get('email')
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/update-profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            updateUserInfo();
            showNotification('Profile updated successfully!', 'success');
        } else {
            showNotification(data.error || 'Profile update failed', 'error');
        }
    } catch (error) {
        console.error('Profile update error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

async function handlePasswordChange(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const passwordData = {
        current_password: formData.get('current_password'),
        new_password: formData.get('new_password')
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(passwordData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            e.target.reset();
            showNotification('Password changed successfully!', 'success');
        } else {
            showNotification(data.error || 'Password change failed', 'error');
        }
    } catch (error) {
        console.error('Password change error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

// Modals
function openTaskModal(task = null) {
    const modal = document.getElementById('task-modal');
    const title = document.getElementById('task-modal-title');
    const body = modal.querySelector('.modal-body');
    
    title.textContent = task ? 'Edit Task' : 'Create Task';
    
    body.innerHTML = `
        <form id="task-form">
            <div class="form-group">
                <label for="task-title">Title</label>
                <input type="text" id="task-title" name="title" value="${task ? escapeHtml(task.title) : ''}" required>
            </div>
            
            <div class="form-group">
                <label for="task-description">Description</label>
                <textarea id="task-description" name="description" rows="4">${task ? escapeHtml(task.description || '') : ''}</textarea>
            </div>
            
            <div class="form-group">
                <label for="task-status">Status</label>
                <select id="task-status" name="status">
                    <option value="pending" ${task && task.status === 'pending' ? 'selected' : ''}>Pending</option>
                    <option value="in_progress" ${task && task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                    <option value="completed" ${task && task.status === 'completed' ? 'selected' : ''}>Completed</option>
                    <option value="cancelled" ${task && task.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="task-priority">Priority</label>
                <select id="task-priority" name="priority">
                    <option value="low" ${task && task.priority === 'low' ? 'selected' : ''}>Low</option>
                    <option value="medium" ${task && task.priority === 'medium' ? 'selected' : ''}>Medium</option>
                    <option value="high" ${task && task.priority === 'high' ? 'selected' : ''}>High</option>
                    <option value="urgent" ${task && task.priority === 'urgent' ? 'selected' : ''}>Urgent</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="task-due-date">Due Date</label>
                <input type="datetime-local" id="task-due-date" name="due_date" 
                       value="${task && task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : ''}">
            </div>
            
            <div class="form-group admin-only ${currentUser && ['admin', 'superadmin'].includes(currentUser.role) ? 'show' : ''}">
                <label for="task-assignee">Assignee</label>
                <select id="task-assignee" name="assignee_uid">
                    <option value="">Unassigned</option>
                </select>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">
                    ${task ? 'Update Task' : 'Create Task'}
                </button>
                ${task ? '<button type="button" class="btn btn-secondary" onclick="deleteTask(' + task.id + ')">Delete Task</button>' : ''}
            </div>
        </form>
    `;
    
    // Load users for assignee dropdown
    if (currentUser && ['admin', 'superadmin'].includes(currentUser.role)) {
        loadUsersForSelect('task-assignee', task ? task.assignee_uid : null);
    }
    
    // Setup form handler
    document.getElementById('task-form').addEventListener('submit', (e) => handleTaskSubmit(e, task));
    
    modal.classList.add('active');
}

function openUserModal(user = null) {
    if (!currentUser || !['admin', 'superadmin'].includes(currentUser.role)) {
        return;
    }
    
    const modal = document.getElementById('user-modal');
    const title = document.getElementById('user-modal-title');
    const body = modal.querySelector('.modal-body');
    
    title.textContent = user ? 'Edit User' : 'Create User';
    
    body.innerHTML = `
        <form id="user-form">
            <div class="form-group">
                <label for="user-username">Username</label>
                <input type="text" id="user-username" name="username" value="${user ? escapeHtml(user.username) : ''}" required>
            </div>
            
            <div class="form-group">
                <label for="user-email">Email</label>
                <input type="email" id="user-email" name="email" value="${user ? escapeHtml(user.email) : ''}" required>
            </div>
            
            <div class="form-group">
                <label for="user-display-name">Display Name</label>
                <input type="text" id="user-display-name" name="display_name" value="${user ? escapeHtml(user.display_name) : ''}" required>
            </div>
            
            <div class="form-group">
                <label for="user-role">Role</label>
                <select id="user-role" name="role">
                    <option value="user" ${user && user.role === 'user' ? 'selected' : ''}>User</option>
                    <option value="admin" ${user && user.role === 'admin' ? 'selected' : ''}>Admin</option>
                    ${currentUser.role === 'superadmin' ? `<option value="superadmin" ${user && user.role === 'superadmin' ? 'selected' : ''}>Superadmin</option>` : ''}
                </select>
            </div>
            
            ${user ? `
                <div class="form-group">
                    <label for="user-active">Status</label>
                    <select id="user-active" name="is_active">
                        <option value="true" ${user.is_active ? 'selected' : ''}>Active</option>
                        <option value="false" ${!user.is_active ? 'selected' : ''}>Inactive</option>
                    </select>
                </div>
            ` : ''}
            
            <div class="form-group">
                <label for="user-password">Password ${user ? '(leave blank to keep current)' : ''}</label>
                <input type="password" id="user-password" name="password" ${!user ? 'required' : ''}>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">
                    ${user ? 'Update User' : 'Create User'}
                </button>
            </div>
        </form>
    `;
    
    // Setup form handler
    document.getElementById('user-form').addEventListener('submit', (e) => handleUserSubmit(e, user));
    
    modal.classList.add('active');
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

// Form handlers
async function handleTaskSubmit(e, task) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const taskData = {
        title: formData.get('title'),
        description: formData.get('description'),
        status: formData.get('status'),
        priority: formData.get('priority'),
        due_date: formData.get('due_date') || null,
        assignee_uid: formData.get('assignee_uid') || null
    };
    
    try {
        const url = task ? `${API_BASE}/tasks/${task.id}` : `${API_BASE}/tasks`;
        const method = task ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(taskData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeModals();
            showNotification(`Task ${task ? 'updated' : 'created'} successfully!`, 'success');
            
            if (currentView === 'tasks') {
                loadTasks();
            } else if (currentView === 'dashboard') {
                loadDashboard();
            }
        } else {
            showNotification(data.error || `Task ${task ? 'update' : 'creation'} failed`, 'error');
        }
    } catch (error) {
        console.error('Task submit error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

async function handleUserSubmit(e, user) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        display_name: formData.get('display_name'),
        role: formData.get('role')
    };
    
    if (user) {
        userData.is_active = formData.get('is_active') === 'true';
    }
    
    const password = formData.get('password');
    if (password) {
        userData.password = password;
    }
    
    try {
        const url = user ? `${API_BASE}/users/${user.id}` : `${API_BASE}/users`;
        const method = user ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeModals();
            showNotification(`User ${user ? 'updated' : 'created'} successfully!`, 'success');
            loadUsers();
        } else {
            showNotification(data.error || `User ${user ? 'update' : 'creation'} failed`, 'error');
        }
    } catch (error) {
        console.error('User submit error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

// Helper functions
async function loadUsersForSelect(selectId, selectedUserId = null) {
    try {
        const response = await fetch(`${API_BASE}/users`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            const select = document.getElementById(selectId);
            
            // Clear existing options except the first one
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.display_name;
                if (user.id === selectedUserId) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Load users for select error:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            closeModals();
            showNotification('Task deleted successfully!', 'success');
            
            if (currentView === 'tasks') {
                loadTasks();
            } else if (currentView === 'dashboard') {
                loadDashboard();
            }
        } else {
            showNotification('Failed to delete task', 'error');
        }
    } catch (error) {
        console.error('Delete task error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

function showNotification(message, type = 'info') {
    const container = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

