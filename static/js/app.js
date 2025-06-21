// Main application script for Smart Reminder Pro
// This file serves as the entry point for client-side functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartReminder app initialized');
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('Service Worker registrert med scope:', registration.scope);
                    
                    // Check for updates
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        console.log('Service Worker oppdatering funnet!');
                        
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                // New content is available
                                showUpdateNotification();
                            }
                        });
                    });
                })
                .catch(error => {
                    console.error('Service Worker registrering feilet:', error);
                });
        });
    }
    
    // Install prompt handling
    let deferredPrompt;
    const installPrompt = document.querySelector('.install-prompt');
    const addBtn = document.querySelector('.add-to-home');
    
    // Hide install prompt by default
    if (installPrompt) {
        installPrompt.style.display = 'none';
    }
    
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        
        // Show install prompt if not installed
        if (installPrompt && !isAppInstalled()) {
            installPrompt.style.display = 'block';
        }
        
        if (addBtn) {
            addBtn.addEventListener('click', async () => {
                // Hide install prompt
                installPrompt.style.display = 'none';
                
                // Show the prompt
                deferredPrompt.prompt();
                
                try {
                    // Wait for the user to respond to the prompt
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`User ${outcome} app installation`);
                    
                    if (outcome === 'accepted') {
                        console.log('App installert');
                        localStorage.setItem('appInstalled', 'true');
                    }
                    
                    // Clear the deferredPrompt
                    deferredPrompt = null;
                } catch (error) {
                    console.error('Feil under app-installasjon:', error);
                }
            });
        }
    });
    
    // Listen for successful installation
    window.addEventListener('appinstalled', (evt) => {
        console.log('App installert vellykket');
        localStorage.setItem('appInstalled', 'true');
        if (installPrompt) {
            installPrompt.style.display = 'none';
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
    // Show update notification to user
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <div class="alert alert-info alert-dismissible fade show" role="alert">
            <strong>Oppdatering tilgjengelig!</strong> 
            En ny versjon av appen er tilgjengelig. 
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            <button onclick="location.reload()" class="btn btn-primary btn-sm ms-2">
                Oppdater nå
            </button>
        </div>
    `;
    document.body.insertBefore(notification, document.body.firstChild);
}

function isAppInstalled() {
    // Check if app is installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
        return true;
    }
    return localStorage.getItem('appInstalled') === 'true';
}

// Handle offline/online status
window.addEventListener('online', function() {
    document.body.classList.remove('offline');
    showConnectivityStatus('online');
});

window.addEventListener('offline', function() {
    document.body.classList.add('offline');
    showConnectivityStatus('offline');
});

function showConnectivityStatus(status) {
    const statusDiv = document.createElement('div');
    statusDiv.className = `connectivity-status ${status}`;
    statusDiv.innerHTML = status === 'online' 
        ? '<i class="fas fa-wifi"></i> Du er tilkoblet igjen'
        : '<i class="fas fa-wifi-slash"></i> Du er offline';
    
    document.body.appendChild(statusDiv);
    setTimeout(() => statusDiv.remove(), 3000);
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
}