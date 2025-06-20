import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade_database():
    # Database connection
    conn = sqlite3.connect('smartreminder.db')
    
    cursor = conn.cursor()
    
    try:
        # SQL kommandoer for SQLite
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                app_mode TEXT DEFAULT 'DEFAULT',
                notification_advance INTEGER DEFAULT 30,
                email_notifications INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                date TIMESTAMP NOT NULL,
                completed INTEGER DEFAULT 0,
                notification_sent INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE DEFAULT CURRENT_DATE,
                reminders_completed INTEGER DEFAULT 0,
                focus_sessions_completed INTEGER DEFAULT 0,
                total_focus_time INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                profile_type TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                profile_type TEXT DEFAULT 'standard',
                preferences TEXT DEFAULT '{"notifications": true, "daily_goal": 5}',
                accessibility_settings TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        ]
        
        # Kjør hver kommando
        for command in sql_commands:
            cursor.execute(command)
            print(f"✅ Executed: {command[:50]}...")
        
        # Legg til kolonner i reminders (med error handling)
        alter_commands = [
            "ALTER TABLE reminders ADD COLUMN difficulty_level INTEGER DEFAULT 1;",
            "ALTER TABLE reminders ADD COLUMN estimated_duration INTEGER DEFAULT 15;",
            "ALTER TABLE reminders ADD COLUMN energy_level TEXT DEFAULT 'medium';",
            "ALTER TABLE reminders ADD COLUMN context_tags TEXT;"
        ]
        alter_commands.append("ALTER TABLE user_statistics ADD COLUMN points INTEGER DEFAULT 0;")
        
        for command in alter_commands:
            try:
                cursor.execute(command)
                print(f"✅ Added column: {command}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Column might already exist: {e}")
        
        conn.commit()
        print("🎉 Database upgrade completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    upgrade_database()
