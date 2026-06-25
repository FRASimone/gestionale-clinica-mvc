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
    
    # Creazione Tabella Prestazione
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Prestazione (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomePrestazione TEXT NOT NULL,
            durataMinuti INTEGER NOT NULL,
            costoBase REAL NOT NULL
        )
    ''')

    # Creazione Tabella Memo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Memo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataInvioProgrammata TEXT NOT NULL,
            inviato INTEGER DEFAULT 0 -- 0 per False, 1 per True
        )
    ''')

    # Creazione Tabella ValutazioneFunzionale
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ValutazioneFunzionale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anomalie TEXT,
            noteAggiuntive TEXT,
            prevOvertraining TEXT,
            valutazioneClinica INTEGER,
            id_cartella INTEGER -- Predisposizione per la futura Cartella Clinica
        )
    ''')
    
    # Creazione Tabella Cartella Clinica
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CartellaClinica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anamnesiGenerica TEXT,
            dataCreazione TEXT NOT NULL,
            cf_paziente TEXT UNIQUE NOT NULL,
            FOREIGN KEY (cf_paziente) REFERENCES Paziente(cf)
        )
    ''')

    # Ricreazione Tabella Appuntamento (Allineata all'UML)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Appuntamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            oraInizio TEXT NOT NULL,
            stato TEXT NOT NULL,
            cf_paziente TEXT NOT NULL,
            id_medico INTEGER NOT NULL,
            id_prestazione INTEGER NOT NULL,
            id_memo INTEGER, -- Può essere NULL (Cardinalità 0..1)
            id_valutazione INTEGER, -- Può essere NULL (Cardinalità 0..1)
            FOREIGN KEY (cf_paziente) REFERENCES Paziente(cf),
            FOREIGN KEY (id_medico) REFERENCES Dipendente(id),
            FOREIGN KEY (id_prestazione) REFERENCES Prestazione(id),
            FOREIGN KEY (id_memo) REFERENCES Memo(id),
            FOREIGN KEY (id_valutazione) REFERENCES ValutazioneFunzionale(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database inizializzato con successo in:", DB_PATH)

# Se eseguiamo questo file direttamente, crea le tabelle.
if __name__ == "__main__":
    inizializza_database()