document.body.addEventListener('htmx:configRequest', function(evt) {
    // Add a custom header to all HTMX requests
    evt.detail.headers['X-Request-Type'] = 'HTMX';
});

document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    // Update unread count after any HTMX response
    updateUnreadCount();
});

function updateUnreadCount() {
    // Count unread notifications in the DOM
    const unreadCount = document.querySelectorAll('.notification.unread').length;
    
    // Update all badges
    updateBadge('.navbar .badge', unreadCount);
    updateBadge('.sidebar .badge', unreadCount);
    updateBadge('.unread-badge', unreadCount, count => count + ' New');
}

function updateBadge(selector, count, formatFn) {
    const badge = document.querySelector(selector);
    if (badge) {
        if (count > 0) {
            badge.style.display = '';
            badge.textContent = formatFn ? formatFn(count) : count;
        } else {
            badge.style.display = 'none';
        }
    }
}