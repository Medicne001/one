// ========== 全局变量 ==========
let todos = [];
let filteredTodos = [];
let currentFilter = 'all';
let currentSort = 'newest';

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    setupEventListeners();
});

// ========== 事件监听 ==========
function setupEventListeners() {
    // 添加任务
    document.getElementById('add-todo-form').addEventListener('submit', handleAddTodo);

    // 筛选按钮
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleFilter);
    });

    // 排序按钮
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.addEventListener('click', handleSort);
    });
}

// ========== 加载任务 ==========
async function loadTodos() {
    try {
        const response = await fetch('/api/todos');
        todos = await response.json();
        applyFilterAndSort();
        updateStats();
    } catch (error) {
        console.error('加载任务失败:', error);
        showNotification('加载任务失败', 'error');
    }
}

// ========== 添加任务 ==========
async function handleAddTodo(e) {
    e.preventDefault();

    const title = document.getElementById('todo-title').value.trim();
    const description = document.getElementById('todo-description').value.trim();
    const priority = document.getElementById('todo-priority').value;

    if (!title) {
        showNotification('请输入任务标题', 'error');
        return;
    }

    try {
        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                description,
                priority
            })
        });

        if (response.ok) {
            const newTodo = await response.json();
            todos.push(newTodo);
            applyFilterAndSort();
            updateStats();
            
            // 清空表单
            document.getElementById('add-todo-form').reset();
            showNotification('✅ 任务已添加', 'success');
        } else {
            showNotification('添加任务失败', 'error');
        }
    } catch (error) {
        console.error('添加任务失败:', error);
        showNotification('添加任务失败', 'error');
    }
}

// ========== 切换任务完成状态 ==========
async function toggleTodo(id) {
    try {
        const response = await fetch(`/api/todos/${id}/toggle`, {
            method: 'PUT'
        });

        if (response.ok) {
            const updatedTodo = await response.json();
            const index = todos.findIndex(t => t.id === id);
            if (index !== -1) {
                todos[index] = updatedTodo;
                applyFilterAndSort();
                updateStats();
                showNotification(updatedTodo.completed ? '✅ 任务已完成' : '📝 任务未完成', 'success');
            }
        }
    } catch (error) {
        console.error('切换任务状态失败:', error);
        showNotification('操作失败', 'error');
    }
}

// ========== 删除任务 ==========
async function deleteTodo(id) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/todos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            todos = todos.filter(t => t.id !== id);
            applyFilterAndSort();
            updateStats();
            showNotification('✅ 任务已删除', 'success');
        }
    } catch (error) {
        console.error('删除任务失败:', error);
        showNotification('删除任务失败', 'error');
    }
}

// ========== 筛选 ==========
function handleFilter(e) {
    currentFilter = e.target.dataset.filter;
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    applyFilterAndSort();
}

// ========== 排序 ==========
function handleSort(e) {
    currentSort = e.target.dataset.sort;
    
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    applyFilterAndSort();
}

// ========== 应用筛选和排序 ==========
function applyFilterAndSort() {
    // 筛选
    filteredTodos = todos.filter(todo => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'completed') return todo.completed;
        if (currentFilter === 'pending') return !todo.completed;
    });

    // 排序
    if (currentSort === 'newest') {
        filteredTodos.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (currentSort === 'priority') {
        const priorityMap = { 'high': 0, 'medium': 1, 'low': 2 };
        filteredTodos.sort((a, b) => priorityMap[a.priority] - priorityMap[b.priority]);
    }

    renderTodos();
}

// ========== 渲染任务列表 ==========
function renderTodos() {
    const todosList = document.getElementById('todos-list');

    if (filteredTodos.length === 0) {
        todosList.innerHTML = '<p class="empty-message">暂无任务，添加一个开始吧！</p>';
        return;
    }

    todosList.innerHTML = filteredTodos.map(todo => `
        <div class="todo-item ${todo.completed ? 'completed' : ''}">
            <input 
                type="checkbox" 
                class="todo-checkbox" 
                ${todo.completed ? 'checked' : ''}
                onchange="toggleTodo(${todo.id})"
            >
            <div class="todo-content">
                <h3 class="todo-title">${escapeHtml(todo.title)}</h3>
                ${todo.description ? `<p class="todo-description">${escapeHtml(todo.description)}</p>` : ''}
                <div class="todo-meta">
                    <span class="todo-date">📅 ${formatDate(todo.created_at)}</span>
                    <span class="priority-badge ${todo.priority}">${getPriorityLabel(todo.priority)}</span>
                </div>
            </div>
            <div class="todo-actions">
                <button class="btn-sm btn-delete" onclick="deleteTodo(${todo.id})">🗑️ 删除</button>
            </div>
        </div>
    `).join('');
}

// ========== 更新统计 ==========
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('total-count').textContent = stats.total;
        document.getElementById('completed-count').textContent = stats.completed;
        document.getElementById('pending-count').textContent = stats.pending;
    } catch (error) {
        console.error('更新统计失败:', error);
    }
}

// ========== 工具函数 ==========
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        const hours = date.getHours();
        const minutes = date.getMinutes();
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    }
    
    if (diffDays === 1) return '昨天';
    if (diffDays < 7) return `${diffDays}天前`;
    
    return date.toLocaleDateString('zh-CN');
}

function getPriorityLabel(priority) {
    const labels = {
        'low': '低',
        'medium': '中',
        'high': '高'
    };
    return labels[priority] || priority;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // 简单的通知（可选：升级为 toast 库）
    console.log(`[${type.toUpperCase()}] ${message}`);
}
