document.addEventListener('DOMContentLoaded', function() {
    // Mode selector functionality
    const modeSelector = document.getElementById('mode-selector');
    if (modeSelector) {
        const modeLinks = modeSelector.querySelectorAll('.mode-link');
        const modeForm = document.getElementById('mode-form');
        const modeInput = document.getElementById('app_mode_input');
        
        modeLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const mode = this.getAttribute('data-mode');
                modeInput.value = mode;
                modeForm.submit();
            });
        });
    }
    
    // Format dates to be more user-friendly
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    // Helper to check if a reminder is due soon (within 24 hours)
    function isDueSoon(dateString) {
        const now = new Date();
        const dueDate = new Date(dateString);
        const diff = dueDate - now;
        const hoursDiff = diff / (1000 * 60 * 60);
        return hoursDiff > 0 && hoursDiff <= 24;
    }
    
    // Helper to check if a reminder is overdue
    function isOverdue(dateString) {
        const now = new Date();
        const dueDate = new Date(dateString);
        return dueDate < now;
    }
    
    // Export utilities for other scripts
    window.appUtils = {
        formatDate: formatDate,
        isDueSoon: isDueSoon,
        isOverdue: isOverdue
    };
});

