document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const notesList = document.getElementById('notes-list');
    const notesLoading = document.getElementById('notes-loading');
    const noNotes = document.getElementById('no-notes');
    const saveNoteBtn = document.getElementById('save-note');
    const addNoteModal = new bootstrap.Modal(document.getElementById('addNoteModal'));
    
    // Load notes when notes tab is active
    if (notesList) {
        // Initial load if noteboard tab is active by default
        if (document.querySelector('#noteboard.active')) {
            loadNotes();
        }
        
        // Tab change event - load notes when tab becomes active
        document.querySelector('button[data-bs-target="#noteboard"]').addEventListener('shown.bs.tab', function(e) {
            loadNotes();
        });
    }
    
    // Save new note
    if (saveNoteBtn) {
        saveNoteBtn.addEventListener('click', function() {
            const title = document.getElementById('note-title').value.trim();
            const content = document.getElementById('note-content').value.trim();
            const shareWith = document.getElementById('note-share').value.trim();
            
            if (!title || !content) {
                alert('Title and content are required!');
                return;
            }
            
            const noteData = {
                title: title,
                content: content,
                share_with: shareWith
            };
            
            fetch('/api/notes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(noteData),
            })
            .then(response => response.json())
            .then(data => {
                // Reset form
                document.getElementById('add-note-form').reset();
                
                // Close modal
                addNoteModal.hide();
                
                // Reload notes
                loadNotes();
            })
            .catch(error => {
                console.error('Error adding note:', error);
                alert('Failed to add note. Please try again.');
            });
        });
    }
    
    // Load notes from API
    function loadNotes() {
        if (!notesList) return;
        
        // Clear previous notes (except loading and empty elements)
        const noteCards = notesList.querySelectorAll('.note-card');
        noteCards.forEach(card => card.remove());
        
        notesLoading.classList.remove('d-none');
        noNotes.classList.add('d-none');
        
        fetch('/api/notes')
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                notesLoading.classList.add('d-none');
                
                // Combine own and shared notes
                const notes = [...(data.own_notes || []), ...(data.shared_notes || [])];
                
                if (notes.length === 0) {
                    noNotes.classList.remove('d-none');
                    return;
                }
                
                // Sort notes by creation date (newest first)
                notes.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                
                // Render notes
                notes.forEach(note => {
                    const isOwn = note.creator_email === null || data.own_notes.some(n => n.id === note.id);
                    renderNote(note, isOwn);
                });
            })
            .catch(error => {
                console.error('Error loading notes:', error);
                notesLoading.classList.add('d-none');
                noNotes.querySelector('p').textContent = 'Kunne ikke laste inn notater. Vennligst prøv igjen.';
                noNotes.classList.remove('d-none');
            });
    }
    
    // Render a single note
    function renderNote(note, isOwn) {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';
        
        // Format date
        const createdDate = new Date(note.created_at);
        const formattedDate = createdDate.toLocaleDateString() + ' ' + createdDate.toLocaleTimeString();
        
        // Determine shared status
        const isShared = note.shared_with && note.shared_with.length > 0;
        const sharedClass = isShared ? 'border-primary' : '';
        
        // Create card HTML
        col.innerHTML = `
            <div class="card note-card h-100 ${sharedClass}" data-id="${note.id}">
                ${isShared ? '<span class="shared-badge">Shared</span>' : ''}
                <div class="card-body">
                    <h5 class="card-title">${note.title}</h5>
                    <p class="card-text">${note.content.replace(/\n/g, '<br>')}</p>
                </div>
                <div class="card-footer text-muted">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <small>By: ${note.creator_email || 'You'}</small><br>
                            <small>${formattedDate}</small>
                        </div>
                        ${isOwn && isShared ? 
                            `<small>Shared with ${note.shared_with.length} ${note.shared_with.length === 1 ? 'person' : 'people'}</small>` : 
                            ''}
                    </div>
                </div>
            </div>
        `;
        
        notesList.appendChild(col);
    }
});
