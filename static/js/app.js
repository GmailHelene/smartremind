// Main application script for Smart Reminder Pro
// This file serves as the entry point for client-side functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartReminder app initialized');
    
    // Check for service worker support and register it
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    }
    
    // Load application modules based on current page
    loadPageModules();
    
    // Set up offline detection
    setupOfflineDetection();
});

function loadPageModules() {
    // Determine current page and load appropriate modules
    const path = window.location.pathname;
    
    if (path.includes('/dashboard')) {
        // Load reminders.js and notes.js dynamically
        loadScript('/static/js/reminders.js');
        loadScript('/static/js/notes.js');
    }
}

function loadScript(src) {
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    document.head.appendChild(script);
}

function setupOfflineDetection() {
    // Monitor online/offline status
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

function updateOnlineStatus() {
    const indicator = document.getElementById('connection-indicator');
    if (!indicator) return;
    
    if (navigator.onLine) {
        indicator.classList.remove('offline');
        indicator.classList.add('online');
        indicator.querySelector('.status-text').textContent = 'Online';
    } else {
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        indicator.querySelector('.status-text').textContent = 'Offline';
    }
}