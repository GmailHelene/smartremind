document.addEventListener('DOMContentLoaded', function() {
    // Fjern loading states når siden er lastet
    document.querySelectorAll('.loading-placeholder').forEach(element => {
        element.style.display = 'none';
    });
    document.querySelectorAll('.content-container').forEach(element => {
        element.style.display = 'block';
    });

    // Mode selector functionality
    const modeSelector = document.getElementById('mode-selector');
    if (modeSelector) {
        modeSelector.addEventListener('change', function(e) {
            const mode = this.value;
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/set_mode';
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'app_mode';
            input.value = mode;
            
            const csrf = document.createElement('input');
            csrf.type = 'hidden';
            csrf.name = 'csrf_token';
            csrf.value = document.querySelector('meta[name="csrf-token"]').content;
            
            form.appendChild(csrf);
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
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

