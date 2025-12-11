function updateUnreadCountBadges(unreadCount) {
    // Update all badges that show unread counts
    const badges = [
        {
            selector: '.navbar .badge',
            format: count => count.toString()
        },
        {
            selector: '.sidebar .badge',
            format: count => count.toString()
        },
        {
            selector: '.unread-badge',
            format: count => count + ' New'
        }
    ];

    badges.forEach(({selector, format}) => {
        const element = document.querySelector(selector);
        if (element) {
            if (unreadCount > 0) {
                element.style.display = '';
                element.textContent = format(unreadCount);
            } else {
                element.style.display = 'none';
            }
        }
    });
}

// Listen for both immediate and after-settle triggers
['htmx:afterOnLoad', 'htmx:afterSettle'].forEach(event => {
    document.addEventListener(event, function(evt) {
        const triggerHeader = evt.detail.xhr.getResponseHeader(
            event === 'htmx:afterSettle' ? 'HX-Trigger-After-Settle' : 'HX-Trigger'
        );
        
        if (triggerHeader) {
            try {
                const triggers = JSON.parse(triggerHeader);
                if (triggers.updateUnreadCount !== undefined) {
                    updateUnreadCountBadges(triggers.updateUnreadCount);
                }
            } catch (e) {
                console.error('Error parsing trigger header:', e);
            }
        }
    });
});