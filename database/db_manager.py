import sqlite3
import os

# Definiamo il percorso assoluto in cui verrà salvato il file del database
DB_PATH = os.path.join(os.path.dirname(__file__), 'clinica.db')

def get_connection():
    """Restituisce una connessione attiva al database SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Imposta la restituzione delle righe come dizionari
    conn.row_factory = sqlite3.Row 
    return conn

def inizializza_database():
    try:
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
        
        # Tabella delle Specializzazioni
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Specializzazione (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                dettagli testuali TEXT
            )
        ''')

        # Tabella Ponte per gestire la relazione Molti-a-Molti
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Medico_Specializzazione (
                id_medico INTEGER NOT NULL,
                id_specializzazione INTEGER NOT NULL,
                PRIMARY KEY (id_medico, id_specializzazione),
                FOREIGN KEY (id_medico) REFERENCES Dipendente(id),
                FOREIGN KEY (id_specializzazione) REFERENCES Specializzazione(id)
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
    # Creazione Tabella Pagamento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pagamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appuntamento_id INTEGER NOT NULL UNIQUE, 
                dataOraPagamento TEXT NOT NULL,
                importo REAL NOT NULL,
                metodo TEXT NOT NULL, 
                FOREIGN KEY (appuntamento_id) REFERENCES Appuntamento(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Fattura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pagamento_id INTEGER NOT NULL UNIQUE, 
                cf_paziente TEXT NOT NULL,
                numeroFattura TEXT NOT NULL UNIQUE,
                dataOraEmissione TEXT NOT NULL,
                totale REAL NOT NULL,
                FOREIGN KEY (pagamento_id) REFERENCES Pagamento(id),
                FOREIGN KEY (cf_paziente) REFERENCES Paziente(cf)
            )
        ''')
        # Creazione Tabella Report
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Report (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                annoRiferimento INTEGER NOT NULL,
                meseRiferimento INTEGER, -- Può essere NULL (o 0) per i report puramente annuali
                tipoReport TEXT NOT NULL,
                datiAggregati TEXT NOT NULL -- Il dizionario Python verrà salvato qui come stringa JSON
            )
        ''')
        

        conn.commit()
        print("Database inizializzato con successo in:", DB_PATH)
    except sqlite3.Error as e:
        print(f"ERRORE: Impossibile inizializzare il database. Dettagli: {e}")
    finally:
        # Il blocco finally garantisce che la connessione venga chiusa SEMPRE,
        # sia che vada a buon fine, sia che ci sia stato un errore.
        conn.close()

# Se eseguiamo questo file direttamente, crea le tabelle.
if __name__ == "__main__":
    inizializza_database()