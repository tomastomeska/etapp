/* European Transport CZ - Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializace Socket.IO pro real-time komunikaci
    if (typeof io !== 'undefined') {
        const socket = io();
        
        socket.on('connect', function() {
            console.log('Připojeno k serveru');
        });
        
        // Příjem notifikací
        socket.on('notification', function(data) {
            showNotification(data.message, data.type || 'info');
        });
        
        // Aktualizace online uživatelů
        socket.on('user_online', function(data) {
            updateUserStatus(data.user_id, 'online');
        });
        
        socket.on('user_offline', function(data) {
            updateUserStatus(data.user_id, 'offline');
        });
    }
    
    // Automatické skrytí flash zpráv po 5 sekundách
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s';
                setTimeout(() => {
                    alert.remove();
                }, 500);
            }, 5000);
        }
    });
    
    // Potvrzení před smazáním
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const confirmMessage = this.dataset.confirm || 'Opravdu chcete tuto položku smazat?';
            if (confirm(confirmMessage)) {
                // Pokud má tlačítko data-url, pošli AJAX request
                if (this.dataset.url) {
                    deleteItem(this.dataset.url);
                } else if (this.form) {
                    this.form.submit();
                }
            }
        });
    });
    
    // Like/Unlike funkcionalita pro novinky
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.dataset.newsId;
            toggleLike(newsId, this);
        });
    });
    
    // Auto-refresh pro notifikace
    setInterval(checkNewMessages, 60000); // Každou minutu
    
    // Tooltip aktivace
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Časové razítka - převod na lokální čas
    const timestamps = document.querySelectorAll('.timestamp');
    timestamps.forEach(timestamp => {
        const utcTime = timestamp.dataset.utc;
        if (utcTime) {
            const localTime = new Date(utcTime).toLocaleString();
            timestamp.textContent = localTime;
        }
    });
});

/**
 * Zobrazení notifikace
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove po 5 sekundách
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * AJAX smazání položky
 */
function deleteItem(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            // Refresh stránky nebo odstraň element
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Došlo k chybě', 'danger');
        }
    })
    .catch(error => {
        console.error('Chyba:', error);
        showNotification('Došlo k chybě při komunikaci se serverem', 'danger');
    });
}

/**
 * Toggle like/unlike pro novinky
 */
function toggleLike(newsId, button) {
    const url = `/like_news/${newsId}`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        // Aktualizace UI
        const icon = button.querySelector('i');
        const counter = button.querySelector('.like-count');
        
        if (data.liked) {
            button.classList.add('liked');
            icon.classList.remove('far');
            icon.classList.add('fas');
        } else {
            button.classList.remove('liked');
            icon.classList.remove('fas');
            icon.classList.add('far');
        }
        
        if (counter) {
            counter.textContent = data.likes_count;
        }
    })
    .catch(error => {
        console.error('Chyba:', error);
        showNotification('Došlo k chybě při hodnocení', 'danger');
    });
}

/**
 * Hlasování v anketách
 */
function voteInPoll(pollId, optionId) {
    const url = `/vote/${pollId}/${optionId}`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Váš hlas byl zaznamenán', 'success');
            // Refresh výsledků ankety
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Došlo k chybě', 'danger');
        }
    })
    .catch(error => {
        console.error('Chyba:', error);
        showNotification('Došlo k chybě při hlasování', 'danger');
    });
}

/**
 * Kontrola nových zpráv
 */
function checkNewMessages() {
    fetch('/api/messages?type=received&per_page=1', {
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        const badge = document.querySelector('.message-badge');
        if (badge && data.unread_count > 0) {
            badge.textContent = data.unread_count;
            badge.style.display = 'inline';
        } else if (badge) {
            badge.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Chyba při kontrole zpráv:', error);
    });
}

/**
 * Aktualizace statusu uživatele
 */
function updateUserStatus(userId, status) {
    const userElements = document.querySelectorAll(`[data-user-id="${userId}"]`);
    userElements.forEach(element => {
        const statusDot = element.querySelector('.status-dot');
        const statusText = element.querySelector('.status-text');
        
        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
        
        if (statusText) {
            statusText.className = `status-text status-${status}`;
            statusText.textContent = status === 'online' ? 'Online' : 
                                   status === 'away' ? 'Nepřítomen' : 'Offline';
        }
    });
}

/**
 * Získání CSRF tokenu
 */
function getCSRFToken() {
    const token = document.querySelector('meta[name=csrf-token]');
    return token ? token.getAttribute('content') : '';
}

/**
 * Formátování času
 */
function timeAgo(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'právě teď';
    if (minutes < 60) return `před ${minutes} min`;
    if (hours < 24) return `před ${hours} h`;
    if (days < 7) return `před ${days} dny`;
    
    return new Date(date).toLocaleDateString();
}

/**
 * Lazy loading obrázků
 */
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

/**
 * Form validace
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
        
        // Email validace
        if (input.type === 'email' && input.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

/**
 * Auto-save pro formuláře
 */
function enableAutoSave(formId, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const saveData = () => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    };
    
    const loadData = () => {
        const savedData = localStorage.getItem(`autosave_${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.entries(data).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'password') {
                    input.value = value;
                }
            });
        }
    };
    
    // Načtení uložených dat při načtení stránky
    loadData();
    
    // Automatické ukládání
    setInterval(saveData, interval);
    
    // Ukládání při změnách
    form.addEventListener('input', saveData);
    
    // Vymazání po odeslání
    form.addEventListener('submit', () => {
        localStorage.removeItem(`autosave_${formId}`);
    });
}

/**
 * Přepnutí tématu (světlé/tmavé)
 */
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
}

// Načtení uloženého tématu
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
}