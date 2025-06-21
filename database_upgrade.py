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
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                date DATE DEFAULT CURRENT_DATE,
                reminders_completed INTEGER DEFAULT 0,
                focus_sessions_completed INTEGER DEFAULT 0,
                total_focus_time INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                profile_type VARCHAR(50)
            );
            """
        ]
        
        # Kjør hver kommando
        for command in sql_commands:
            cursor.execute(command)
            print(f"✅ Executed: {command[:50]}...")
        
        # Legg til kolonner i reminders (med error handling)
        alter_commands = [
            "ALTER TABLE reminders ADD COLUMN IF NOT EXISTS difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 3);",
            "ALTER TABLE reminders ADD COLUMN IF NOT EXISTS estimated_duration INTEGER DEFAULT 15;",
            "ALTER TABLE reminders ADD COLUMN IF NOT EXISTS energy_level VARCHAR(20) DEFAULT 'medium';",
            "ALTER TABLE reminders ADD COLUMN IF NOT EXISTS context_tags TEXT[];"
        ]
        alter_commands.append("ALTER TABLE user_statistics ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0;")
        
        for command in alter_commands:
            try:
                cursor.execute(command)
                print(f"✅ Added column: {command}")
            except psycopg2.Error as e:
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
