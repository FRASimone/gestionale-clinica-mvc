import sqlite3

def popola_database(db_path="database/clinica.db"):
    """
    Script di Seeding: Inserisce i dati iniziali di base nel database.
    Se i dati esistono già, non fa nulla per evitare duplicati.
    """
    print("Avvio popolamento del database...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- 1. INSERIMENTO PERSONALE BASE ---
        # Creiamo una password standard che rispetti il vostro requisito dei >8 caratteri
        password_standard = "password123"

        dipendenti_base = [
            ("Admin", "Supremo", "admin@clinica.it", password_standard, "Amministratore"),
            ("Mario", "Rossi", "medico@clinica.it", password_standard, "Medico"),
            ("Giulia", "Bianchi", "segreteria@clinica.it", password_standard, "Segretario")
        ]

        print("- Inserimento Dipendenti...")
        for nome, cognome, email, password, ruolo in dipendenti_base:
            try:
                cursor.execute(
                    "INSERT INTO Dipendente (nome, cognome, email, password, ruolo) VALUES (?, ?, ?, ?, ?)",
                    (nome, cognome, email, password, ruolo)
                )
            except sqlite3.IntegrityError:
                # L'email è UNIQUE. Se l'utente esiste già, lo ignoriamo silenziosamente
                pass


        # --- 2. INSERIMENTO LISTINO PRESTAZIONI ---
        prestazioni_base = [
            ("Visita Medica di Controllo", 30, 50.00),
            ("Visita Sportiva Agonistica", 45, 75.00),
            ("Elettrocardiogramma (ECG)", 20, 35.00),
            ("Valutazione Funzionale", 60, 90.00)
        ]

        print("- Inserimento Prestazioni...")
        # Per le prestazioni, controlliamo prima se la tabella è vuota per non duplicarle
        cursor.execute("SELECT COUNT(*) FROM Prestazione")
        if cursor.fetchone()[0] == 0:
            for nome, durata, costo in prestazioni_base:
                cursor.execute(
                    "INSERT INTO Prestazione (nomePrestazione, durataMinuti, costoBase) VALUES (?, ?, ?)",
                    (nome, durata, costo)
                )
        else:
            print("  (Prestazioni già presenti, salto l'inserimento)")
            
        # --- 3. INSERIMENTO SPECIALIZZAZIONI ---
        specializzazioni_base = [
            ("Cardiologia", "Malattie del cuore e vasi sanguigni"),
            ("Ortopedia", "Sistema muscolo-scheletrico"),
            ("Medicina dello Sport", "Prevenzione e cura per atleti"),
            ("Neurologia", "Sistema nervoso centrale e periferico")
        ]

        print("- Inserimento Specializzazioni...")
        cursor.execute("SELECT COUNT(*) FROM Specializzazione")
        if cursor.fetchone()[0] == 0:
            for nome, dettagli in specializzazioni_base:
                cursor.execute(
                    "INSERT INTO Specializzazione (nome, dettagli) VALUES (?, ?)",
                    (nome, dettagli)
                )
        else:
            print("  (Specializzazioni già presenti, salto l'inserimento)")

        conn.commit()
        conn.close()
        print("\n✅ Popolamento completato con successo! Il sistema è pronto per i test.")

    except Exception as e:
        print(f"\n❌ Errore durante il popolamento: {e}")

if __name__ == "__main__":
    popola_database()