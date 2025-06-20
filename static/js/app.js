// Main application script for Smart Reminder Pro
// This file serves as the entry point for client-side functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartReminder app initialized');
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered with scope:', registration.scope);
                    
                    // Check for updates
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        console.log('Service Worker update found!');
                        
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                // New content is available
                                showUpdateNotification();
                            }
                        });
                    });
                })
                .catch(error => {
                    console.error('Service Worker registration failed:', error);
                });
        });
    }
    
    // Install prompt
    let deferredPrompt;
    const addBtn = document.querySelector('.add-to-home');
    
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        // Update UI to notify the user they can add to home screen
        if (addBtn) {
            addBtn.style.display = 'block';
            
            addBtn.addEventListener('click', () => {
                // Show the prompt
                deferredPrompt.prompt();
                // Wait for the user to respond to the prompt
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('User accepted the A2HS prompt');
                    }
                    deferredPrompt = null;
                });
            });
        }
    });
    
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
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        
        script.onload = () => resolve(script);
        script.onerror = () => reject(new Error(`Script load error for ${src}`));
        
        document.head.appendChild(script);
    });
}

function setupOfflineDetection() {
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

function updateOnlineStatus() {
    const statusDisplay = document.getElementById('connection-status');
    if (statusDisplay) {
        if (navigator.onLine) {
            statusDisplay.textContent = 'Online';
            statusDisplay.classList.remove('offline');
            statusDisplay.classList.add('online');
            syncOfflineData();
        } else {
            statusDisplay.textContent = 'Offline';
            statusDisplay.classList.remove('online');
            statusDisplay.classList.add('offline');
        }
    }
}

function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <p>En ny versjon er tilgjengelig!</p>
        <button onclick="window.location.reload()">Oppdater nå</button>
    `;
    document.body.appendChild(notification);
}

async function syncOfflineData() {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        try {
            const registration = await navigator.serviceWorker.ready;
            await registration.sync.register('sync-reminders');
        } catch (err) {
            console.error('Background sync failed:', err);
        }
    }
}{
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