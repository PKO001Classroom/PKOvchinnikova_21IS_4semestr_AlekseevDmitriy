// Основной JavaScript файл для системы управления учебным процессом

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initTooltips();
    initPopovers();
    initFormsValidation();
    initDynamicForms();
    
    // Обработка HTMX событий
    if (typeof htmx !== 'undefined') {
        initHTMX();
    }
});

// Инициализация тултипов Bootstrap
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация popover Bootstrap
function initPopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Валидация форм
function initFormsValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Динамические формы
function initDynamicForms() {
    // Динамическое обновление зависимых полей
    const dependentSelects = document.querySelectorAll('[data-dependent]');
    
    dependentSelects.forEach(select => {
        const targetId = select.getAttribute('data-dependent');
        const targetSelect = document.getElementById(targetId);
        
        if (targetSelect) {
            select.addEventListener('change', function() {
                updateDependentSelect(this.value, targetSelect, this.getAttribute('data-url'));
            });
        }
    });
    
    // Обработка динамического расчета оценок
    const percentageInputs = document.querySelectorAll('[data-calculate-grade]');
    
    percentageInputs.forEach(input => {
        input.addEventListener('input', function() {
            calculateGradeFromPercentage(this);
        });
    });
}

// Обновление зависимого select
function updateDependentSelect(value, targetSelect, url) {
    if (!value) {
        targetSelect.innerHTML = '<option value="">Выберите...</option>';
        return;
    }
    
    fetch(`${url}?value=${value}`)
        .then(response => response.json())
        .then(data => {
            targetSelect.innerHTML = '<option value="">Выберите...</option>';
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item.name;
                targetSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Расчет оценки из процента
function calculateGradeFromPercentage(input) {
    const percentage = parseInt(input.value) || 0;
    const resultElement = document.querySelector(input.getAttribute('data-target'));
    
    if (!resultElement) return;
    
    let grade, level, color;
    
    if (percentage >= 86 && percentage <= 100) {
        grade = 5;
        level = "высокий уровень";
        color = "success";
    } else if (percentage >= 67 && percentage <= 85) {
        grade = 4;
        level = "повышенный уровень";
        color = "primary";
    } else if (percentage >= 48 && percentage <= 66) {
        grade = 3;
        level = "базовый уровень";
        color = "warning";
    } else if (percentage >= 0 && percentage <= 47) {
        grade = 2;
        level = "не сформировано";
        color = "danger";
    } else {
        grade = "?";
        level = "некорректный процент";
        color = "secondary";
    }
    
    resultElement.textContent = `${grade} (${level})`;
    resultElement.className = `badge bg-${color}`;
    
    // Валидация ввода
    if (percentage >= 0 && percentage <= 100) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
}

// Инициализация HTMX
function initHTMX() {
    // Добавление CSRF токена к HTMX запросам
    htmx.on('htmx:configRequest', (event) => {
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            event.detail.headers['X-CSRFToken'] = csrfToken;
        }
    });
    
    // Обработка успешных запросов
    htmx.on('htmx:afterRequest', (event) => {
        if (event.detail.successful) {
            // Переинициализация компонентов после загрузки контента
            setTimeout(() => {
                initTooltips();
                initPopovers();
            }, 100);
        }
    });
    
    // Показать/скрыть спиннер при загрузке
    htmx.on('htmx:beforeRequest', (event) => {
        const target = event.detail.target;
        if (target) {
            target.classList.add('loading');
        }
    });
    
    htmx.on('htmx:afterRequest', (event) => {
        const target = event.detail.target;
        if (target) {
            target.classList.remove('loading');
        }
    });
}

// Утилитарные функции
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API функции
async function fetchStudentGrades(studentId) {
    try {
        const response = await fetch(`/api/student/${studentId}/grades/`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching student grades:', error);
        return { grades: [] };
    }
}

async function fetchSubjectStatistics(subjectId) {
    try {
        const response = await fetch(`/api/subject/${subjectId}/statistics/`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching subject statistics:', error);
        return {};
    }
}

// UI функции
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    const toast = createToast(message, type);
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1055;';
    document.body.appendChild(container);
    return container;
}

function createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-' + type;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    return toast;
}

// Экспорт данных
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let row of rows) {
        let cols = row.querySelectorAll('td, th');
        let rowData = [];
        
        for (let col of cols) {
            let text = col.textContent.trim();
            text = text.replace(/\s+/g, ' ').replace(/,/g, ';');
            rowData.push(text);
        }
        
        csv.push(rowData.join(","));
    }
    
    downloadCSV(csv.join("\n"), filename);
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Глобальные функции для использования в шаблонах
window.EduSystem = {
    showToast,
    exportTableToCSV,
    fetchStudentGrades,
    fetchSubjectStatistics,
    formatDate,
    calculateGradeFromPercentage
};