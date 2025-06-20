document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const remindersList = document.getElementById('reminders-list');
    const sharedRemindersList = document.getElementById('shared-reminders-list');
    const remindersLoading = document.getElementById('reminders-loading');
    const noReminders = document.getElementById('no-reminders');
    const noSharedReminders = document.getElementById('no-shared-reminders');
    const saveReminderBtn = document.getElementById('save-reminder');
    const addReminderModal = new bootstrap.Modal(document.getElementById('addReminderModal'));
    
    // Load reminders when reminders tab is active
    if (remindersList) {
        loadReminders();
        
        // Tab change event - reload reminders when tab becomes active
        document.querySelector('button[data-bs-target="#reminders"]').addEventListener('shown.bs.tab', function(e) {
            loadReminders();
        });
    }
    
    // Save new reminder
    if (saveReminderBtn) {
        saveReminderBtn.addEventListener('click', function() {
            const title = document.getElementById('reminder-title').value.trim();
            const description = document.getElementById('reminder-description').value.trim();
            const date = document.getElementById('reminder-date').value;
            const shareWith = document.getElementById('reminder-share').value.trim();
            
            if (!title || !date) {
                alert('Tittel og dato er påkrevd!');
                return;
            }
            
            const reminderData = {
                title: title,
                description: description,
                date: new Date(date).toISOString(),
                share_with: shareWith
            };
            
            fetch('/api/reminders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reminderData),
            })
            .then(response => response.json())
            .then(data => {
                // Reset form
                document.getElementById('add-reminder-form').reset();
                
                // Close modal
                addReminderModal.hide();
                
                // Reload reminders
                loadReminders();
            })
            .catch(error => {
                console.error('Error adding reminder:', error);
                alert('Failed to add reminder. Please try again.');
            });
        });
    }
    
    // Load reminders from API
    function loadReminders() {
        if (!remindersList) return;
        
        remindersLoading.classList.remove('d-none');
        noReminders.classList.add('d-none');
        noSharedReminders.classList.add('d-none');
        
        fetch('/api/reminders')
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                remindersLoading.classList.add('d-none');
                
                // Process own reminders
                const ownReminders = data.own_reminders || [];
                renderReminders(ownReminders, remindersList, noReminders);
                
                // Process shared reminders
                const sharedReminders = data.shared_reminders || [];
                renderReminders(sharedReminders, sharedRemindersList, noSharedReminders, true);
            })
            .catch(error => {
                console.error('Error loading reminders:', error);
                remindersLoading.classList.add('d-none');
                noReminders.querySelector('p').textContent = 'Kunne ikke laste inn påminnelser. Vennligst prøv igjen.';
                noReminders.classList.remove('d-none');
            });
    }
    
    // Render reminders to a container
    function renderReminders(reminders, container, emptyMessage, isShared = false) {
        // Clear container (except loading and empty message elements)
        const elements = container.querySelectorAll('.reminder-item');
        elements.forEach(el => el.remove());
        
        if (reminders.length === 0) {
            emptyMessage.classList.remove('d-none');
            return;
        }
        
        emptyMessage.classList.add('d-none');
        
        // Sort reminders by date (nearest first)
        reminders.sort((a, b) => new Date(a.date) - new Date(b.date));
        
        // Add reminders to container
        reminders.forEach(reminder => {
            // Determine CSS classes based on reminder status
            let cardClasses = 'card reminder-item mb-3';
            if (window.appUtils.isOverdue(reminder.date)) {
                cardClasses += ' reminder-overdue';
            } else if (window.appUtils.isDueSoon(reminder.date)) {
                cardClasses += ' reminder-due-soon';
            }
            if (isShared || reminder.shared_with.length > 0) {
                cardClasses += ' reminder-shared';
            }
            
            // Create reminder element
            const reminderEl = document.createElement('div');
            reminderEl.className = cardClasses;
            reminderEl.dataset.id = reminder.id;
            
            // Format shared info text
            let sharedInfo = '';
            if (isShared) {
                sharedInfo = `<div class="text-muted small mt-2">Shared by: ${reminder.owner_email}</div>`;
            } else if (reminder.shared_with.length > 0) {
                sharedInfo = `<div class="text-muted small mt-2">Shared with: ${reminder.shared_with.join(', ')}</div>`;
            }
            
            // Format date and determine status text
            const formattedDate = window.appUtils.formatDate(reminder.date);
            let statusClass = '';
            let statusText = '';
            
            if (window.appUtils.isOverdue(reminder.date)) {
                statusClass = 'text-danger';
                statusText = 'Overdue';
            } else if (window.appUtils.isDueSoon(reminder.date)) {
                statusClass = 'text-warning';
                statusText = 'Due soon';
            }
            
            // Create card content
            reminderEl.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="card-title">${reminder.title}</h5>
                        <span class="badge bg-primary rounded-pill">${statusText}</span>
                    </div>
                    <p class="card-text">${reminder.description || 'No description'}</p>
                    <div class="d-flex justify-content-between">
                        <div class="${statusClass}">Due: ${formattedDate}</div>
                        ${!isShared ? `<button class="btn btn-sm btn-outline-danger delete-reminder" data-id="${reminder.id}">Delete</button>` : ''}
                    </div>
                    ${sharedInfo}
                </div>
            `;
            
            // Add delete event handler
            const deleteBtn = reminderEl.querySelector('.delete-reminder');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const id = this.getAttribute('data-id');
                    if (confirm('Are you sure you want to delete this reminder?')) {
                        deleteReminder(id);
                    }
                });
            }
            
            container.appendChild(reminderEl);
        });
    }
    
    // Delete a reminder
    function deleteReminder(id) {
        fetch(`/api/reminders/${id}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                // Reload reminders after successful deletion
                loadReminders();
            } else {
                throw new Error('Failed to delete reminder');
            }
        })
        .catch(error => {
            console.error('Error deleting reminder:', error);
            alert('Failed to delete reminder. Please try again.');
        });
    }
});
