-- Oppgrader databaseskjema for påminnelser
-- Sikkerhetskopi av eksisterende data
CREATE TABLE IF NOT EXISTS reminders_backup AS SELECT * FROM reminders;

-- Dropp eksisterende tabell
DROP TABLE IF EXISTS reminders;

-- Opprett ny tabell med korrekt skjema
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    datetime DATETIME NOT NULL,  -- Endret fra separate date/time kolonner
    category TEXT,
    priority TEXT,
    completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    shared_with TEXT
);

-- Indekser for raskere spørringer
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_datetime ON reminders(datetime);
CREATE INDEX IF NOT EXISTS idx_reminders_completed ON reminders(completed);

-- Brukerinnstillinger
CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY,
    notification_time INTEGER DEFAULT 30,
    email_notifications TEXT DEFAULT 'all',
    app_mode TEXT DEFAULT 'DEFAULT',
    focus_settings TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Fokusøkter
CREATE TABLE IF NOT EXISTS focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
