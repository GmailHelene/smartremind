import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Sjekk og oppdater databasen"""
    try:
        # Koble til databasen
        conn = sqlite3.connect('smartreminder.db')
        cur = conn.cursor()
        
        # Les og kjør migreringsskript
        with open('migrations/upgrade_001.sql', 'r') as f:
            migration_sql = f.read()
            cur.executescript(migration_sql)
        
        # Sjekk tabellstruktur
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        logger.info(f"Eksisterende tabeller: {[t[0] for t in tables]}")
        
        # Sjekk kolonner i reminders-tabellen
        cur.execute("PRAGMA table_info(reminders)")
        columns = cur.fetchall()
        logger.info(f"Kolonner i reminders-tabellen: {[c[1] for c in columns]}")
        
        conn.commit()
        logger.info("Database sjekket og oppdatert vellykket")
        
        return True
    except Exception as e:
        logger.error(f"Databasefeil: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_database()
