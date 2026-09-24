import sqlite3
from datetime import datetime, timedelta


def popola_database(db_path="database/clinica.db"):
    """
    Script di Seeding: inserisce i dati iniziali di base nel database.
    E' idempotente: se i dati esistono già, non li duplica.
    """
    print("Avvio popolamento del database...")

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- 1. INSERIMENTO PERSONALE BASE ---
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
                pass  # email UNIQUE: utente già presente

        # --- 2. INSERIMENTO LISTINO PRESTAZIONI ---
        prestazioni_base = [
            ("Visita Medica di Controllo", 30, 50.00),
            ("Visita Sportiva Agonistica", 45, 75.00),
            ("Elettrocardiogramma (ECG)", 20, 35.00),
            ("Valutazione Funzionale", 60, 90.00)
        ]

        print("- Inserimento Prestazioni...")
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

        # --- 4. COLLEGAMENTO MEDICO - SPECIALIZZAZIONE ---
        print("- Collegamento Medico-Specializzazione...")
        cursor.execute("SELECT id FROM Dipendente WHERE email = 'medico@clinica.it'")
        medico = cursor.fetchone()
        cursor.execute("SELECT id FROM Specializzazione WHERE nome = 'Cardiologia'")
        specializzazione = cursor.fetchone()

        if medico and specializzazione:
            try:
                cursor.execute(
                    "INSERT INTO Medico_Specializzazione (id_medico, id_specializzazione) VALUES (?, ?)",
                    (medico[0], specializzazione[0])
                )
            except sqlite3.IntegrityError:
                pass  # collegamento già esistente

        # --- 5. INSERIMENTO PAZIENTI FITTIZI ---
        pazienti_base = [
            ("VRDLCU85M20H501A", "Luca", "Verdi", "luca.verdi@email.it", "3331112223", 1),  # Agonista
            ("NRANNA92F45H501B", "Anna", "Neri", "anna.neri@email.it", "3334445556", 0)     # Non agonista
        ]

        print("- Inserimento Pazienti...")
        for cf, nome, cognome, email, telefono, is_agonista in pazienti_base:
            try:
                cursor.execute(
                    "INSERT INTO Paziente (cf, nome, cognome, email, telefono, isAgonista) VALUES (?, ?, ?, ?, ?, ?)",
                    (cf, nome, cognome, email, telefono, is_agonista)
                )
            except sqlite3.IntegrityError:
                pass  # CF già presente

        # --- 6. INSERIMENTO CARTELLE CLINICHE ---
        oggi_str = datetime.now().strftime("%Y-%m-%d")
        cartelle_base = [
            ("Nessuna patologia pregressa. Paziente in salute.", oggi_str, "VRDLCU85M20H501A"),
            ("Lieve ipertensione in cura farmacologica.", oggi_str, "NRANNA92F45H501B")
        ]

        print("- Inserimento Cartelle Cliniche...")
        for anamnesi, data_creazione, cf in cartelle_base:
            try:
                cursor.execute(
                    "INSERT INTO CartellaClinica (anamnesiGenerica, dataCreazione, cf_paziente) VALUES (?, ?, ?)",
                    (anamnesi, data_creazione, cf)
                )
            except sqlite3.IntegrityError:
                pass  # cartella già esistente per questo CF

        # --- 7. INSERIMENTO APPUNTAMENTI ---
        print("- Inserimento Appuntamenti...")
        cursor.execute("SELECT id FROM Prestazione WHERE nomePrestazione = 'Visita Medica di Controllo'")
        id_prestazione_base = cursor.fetchone()
        cursor.execute("SELECT id FROM Prestazione WHERE nomePrestazione = 'Visita Sportiva Agonistica'")
        id_prestazione_sportiva = cursor.fetchone()

        if medico and id_prestazione_base and id_prestazione_sportiva:
            oggi = datetime.now()
            data_domani = (oggi + timedelta(days=1)).strftime("%Y-%m-%d")
            data_dopodomani = (oggi + timedelta(days=2)).strftime("%Y-%m-%d")

            appuntamenti_base = [
                # data, ora, stato, cf_paziente, id_medico, id_prestazione
                (data_domani, "09:00", "Programmato", "VRDLCU85M20H501A", medico[0], id_prestazione_sportiva[0]),
                (data_dopodomani, "10:30", "Programmato", "NRANNA92F45H501B", medico[0], id_prestazione_base[0])
            ]

            inseriti = 0
            for data, ora, stato, cf, id_med, id_prest in appuntamenti_base:
                # Controllo "questo specifico appuntamento esiste già?" al posto
                # del vecchio "la tabella è vuota?", che bloccava tutto se il DB
                # conteneva già qualsiasi appuntamento.
                cursor.execute(
                    """SELECT 1 FROM Appuntamento
                       WHERE data = ? AND oraInizio = ? AND cf_paziente = ? AND id_medico = ?""",
                    (data, ora, cf, id_med)
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        """INSERT INTO Appuntamento
                           (data, oraInizio, stato, cf_paziente, id_medico, id_prestazione)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (data, ora, stato, cf, id_med, id_prest)
                    )
                    inseriti += 1

            print(f"  ({inseriti} nuovi appuntamenti inseriti)")

        # Un solo commit, alla fine, dopo TUTTE le operazioni
        conn.commit()
        print("\n✅ Popolamento completato con successo! Il sistema è pronto per i test.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Errore durante il popolamento: {e}")
    finally:
        # La connessione si chiude sempre, una sola volta, alla fine
        if conn:
            conn.close()


if __name__ == "__main__":
    popola_database()