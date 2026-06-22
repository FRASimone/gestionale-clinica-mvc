import sqlite3
import os

# Definiamo il percorso assoluto in cui verrà salvato il file del database
DB_PATH = os.path.join(os.path.dirname(__file__), 'clinica.db')

def get_connection():
    """Restituisce una connessione attiva al database SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Imposta la restituzione delle righe come dizionari (più comodo per l'MVC)
    conn.row_factory = sqlite3.Row 
    return conn

def inizializza_database():
    """Crea le tabelle fondamentali se non esistono già."""
    conn = get_connection()
    cursor = conn.cursor()

    # Creazione Tabella Dipendente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dipendente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            ruolo TEXT NOT NULL
        )
    ''')

    # Creazione Tabella Paziente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Paziente (
            cf TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            isAgonista BOOLEAN NOT NULL CHECK (isAgonista IN (0, 1))
        )
    ''')

    conn.commit()
    conn.close()
    print("Database inizializzato con successo in:", DB_PATH)

# Se eseguiamo questo file direttamente, crea le tabelle.
if __name__ == "__main__":
    inizializza_database()