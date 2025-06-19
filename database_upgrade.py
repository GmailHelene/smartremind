import os
import psycopg2
from psycopg2 import sql

def upgrade_database():
    # Database connection
    conn = psycopg2.connect(
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD')
    )
    
    cursor = conn.cursor()
    
    try:
        # SQL kommandoer
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                profile_type VARCHAR(50) DEFAULT 'standard',
                preferences JSONB DEFAULT '{}',
                accessibility_settings JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS custom_categories (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                color VARCHAR(7) DEFAULT '#2E86AB',
                icon VARCHAR(50) DEFAULT 'bell',
                profile_specific BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_type VARCHAR(50) DEFAULT 'pomodoro',
                duration_minutes INTEGER DEFAULT 25,
                break_duration INTEGER DEFAULT 5,
                completed BOOLEAN DEFAULT FALSE,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT
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
