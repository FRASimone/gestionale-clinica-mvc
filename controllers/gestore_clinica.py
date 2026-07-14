import sqlite3
from datetime import date, timedelta, datetime

# Importiamo i models che abbiamo appena costruito
from models.prestazione import Prestazione
from models.cartella_clinica import CartellaClinica
from models.appuntamento import Appuntamento

class GestoreClinica:
    def __init__(self, db_path="database/clinica.db"):
        self.db_path = db_path

    def _get_connection(self):
        """Metodo privato per la connessione al database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ==========================================
    # # --- METODI DI SERVIZIO (Non in UML ma necessari per UI/DB) ---
    # ==========================================

    def getPrestazioniDisponibili(self) -> list:
        """
        Recupera tutte le prestazioni dal DB. 
        Servirà all'interfaccia grafica per riempire la tendina (ComboBox) 
        quando il segretario deve scegliere che tipo di visita prenotare.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Prestazione")
        rows = cursor.fetchall()
        conn.close()

        lista_prestazioni = []
        for row in rows:
            prestazione = Prestazione(row['id'], row['nomePrestazione'], row['durataMinuti'], row['costoBase'])
            lista_prestazioni.append(prestazione)
            
        return lista_prestazioni
    
    def creaCartellaClinica(self, cf_paziente: str, anamnesi_generica: str = "") -> tuple:
        """
        Crea la cartella clinica per un nuovo paziente.
        Usa la data odierna generata automaticamente da Python.
        """
        # Creiamo la data di oggi formattata a stringa (YYYY-MM-DD) per il database
        data_creazione_str = date.today().isoformat()
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO CartellaClinica (anamnesiGenerica, dataCreazione, cf_paziente)
                VALUES (?, ?, ?)
            ''', (anamnesi_generica, data_creazione_str, cf_paziente))
            
            conn.commit()
            conn.close()
            return True, "Cartella Clinica generata correttamente."
            
        except sqlite3.IntegrityError:
            # Ricordi l'UNIQUE che abbiamo messo sul CF? Se proviamo a creare due cartelle per lo stesso paziente, scatta questo errore.
            return False, "Il paziente possiede già una Cartella Clinica."
        except sqlite3.Error as e:
            return False, f"Errore del database: {str(e)}"
        
    def getTuttiMedici(self) -> list:
        """Metodo di supporto per la View: recupera i medici per la tendina."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cognome FROM Dipendente WHERE ruolo = 'Medico'")
        medici = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return medici

    def getTuttiPazienti(self) -> list:
        """Metodo di supporto per la View: recupera i pazienti per la tendina."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cf, nome, cognome FROM Paziente")
        pazienti = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pazienti

    # ==========================================
    # SEZIONE 2: CORE BUSINESS
    # ==========================================

    from datetime import date, time, timedelta


    def creaAppuntamento(self, data: date, ora: time, cfPaziente: str, idMedico: int, idPrestazione: int) -> tuple:
        """Crea un appuntamento calcolando la durata e bloccando le sovrapposizioni (RF12)."""
        data_str = data.isoformat()
        ora_str = ora.strftime("%H:%M")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # --- FASE 1: Recupero durata e Calcolo Limiti ---
            # Dobbiamo prima fare la SELECT per definire "durata_nuova"
            cursor.execute("SELECT durataMinuti FROM Prestazione WHERE id = ?", (idPrestazione,))
            prestazione_nuova = cursor.fetchone()
            
            if not prestazione_nuova:
                conn.close()
                return False, "Errore: Prestazione non trovata nel catalogo."
                
            durata_nuova = prestazione_nuova['durataMinuti']
            # Ora possiamo calcolare la fine usando il metodo statico!
            fine_nuovo_str = Appuntamento.calcolaOraFine(ora_str, durata_nuova)
            
            # --- FASE 2a: Verifica Conflitti nell'Agenda del Medico ---
            cursor.execute("""
                SELECT A.oraInizio, P.durataMinuti 
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                WHERE A.id_medico = ? AND A.data = ? AND A.stato != 'Annullato'
            """, (idMedico, data_str))
            
            appuntamenti_medico = cursor.fetchall()
            for app in appuntamenti_medico:
                fine_es_str = Appuntamento.calcolaOraFine(app['oraInizio'], app['durataMinuti'])
                
                if ora_str < fine_es_str and fine_nuovo_str > app['oraInizio']:
                    conn.close()
                    return False, f"Conflitto Medico: Il dottore è già occupato dalle {app['oraInizio']} alle {fine_es_str}."

            # --- FASE 2b: Verifica Conflitti nell'Agenda del Paziente ---
            cursor.execute("""
                SELECT A.oraInizio, P.durataMinuti, M.cognome AS cognome_medico
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                JOIN Dipendente M ON A.id_medico = M.id
                WHERE A.cf_paziente = ? AND A.data = ? AND A.stato != 'Annullato'
            """, (cfPaziente, data_str))
            
            appuntamenti_paziente = cursor.fetchall()
            for app in appuntamenti_paziente:
                fine_es_str = Appuntamento.calcolaOraFine(app['oraInizio'], app['durataMinuti'])
                
                if ora_str < fine_es_str and fine_nuovo_str > app['oraInizio']:
                    conn.close()
                    return False, f"Conflitto Paziente: Ha già una visita (Dott. {app['cognome_medico']}) dalle {app['oraInizio']} alle {fine_es_str}."
            
            # --- FASE 3: Inserimento ---
            cursor.execute('''
                INSERT INTO Appuntamento 
                (data, oraInizio, stato, cf_paziente, id_medico, id_prestazione, id_memo, id_valutazione) 
                VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            ''', (data_str, ora_str, "Programmato", cfPaziente, idMedico, idPrestazione))
            
            conn.commit()
            conn.close()
            # Usiamo fine_nuovo_str direttamente senza fare .strftime()
            return True, f"Appuntamento confermato.\n(Durata prevista: {durata_nuova} min. Fine: {fine_nuovo_str})"
            
        except sqlite3.Error as e:
            print(f"Errore creazione appuntamento: {e}")
            return False, "Errore generico del database durante la prenotazione."
        
    def getDettagliAppuntamento(self, id_appuntamento: int) -> dict:
        """Recupera i dettagli di un singolo appuntamento per pre-compilare l'interfaccia di modifica."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT A.id, A.data, A.oraInizio, P.nome, P.cognome 
            FROM Appuntamento A
            JOIN Paziente P ON A.cf_paziente = P.cf
            WHERE A.id = ?
        """
        cursor.execute(query, (id_appuntamento,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}
    
    def annullaAppuntamento(self, idAppuntamento: int) -> bool:
            """Cambia lo stato dell'appuntamento in Annullato."""
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE Appuntamento SET stato = 'Annullato' WHERE id = ?", (idAppuntamento,))
                conn.commit()
                righe_modificate = cursor.rowcount
                conn.close()
                return righe_modificate > 0
            except sqlite3.Error:
                return False

    def modificaOrarioAppuntamento(self, idAppuntamento: int, nuovaData: date, nuovaOra: time) -> tuple:
        """Aggiorna data e ora di un appuntamento esistente, verificando prima i conflitti orari (RF13)."""
        data_str = nuovaData.isoformat()
        ora_str = nuovaOra.strftime("%H:%M")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # --- FASE 0: Recupero dei dati attuali dell'appuntamento ---
            cursor.execute("""
                SELECT A.cf_paziente, A.id_medico, P.durataMinuti
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                WHERE A.id = ?
            """, (idAppuntamento,))
            app_corrente = cursor.fetchone()
            
            if not app_corrente:
                conn.close()
                return False, "Errore: Appuntamento non trovato nel sistema."
                
            cfPaziente = app_corrente['cf_paziente']
            idMedico = app_corrente['id_medico']
            durata_nuova = app_corrente['durataMinuti']
            
            # --- FASE 1: Calcolo Limiti del Nuovo Orario con metodo statico ---
            fine_nuovo_str = Appuntamento.calcolaOraFine(ora_str, durata_nuova)
            
            # --- FASE 2a: Verifica Conflitti nell'Agenda del Medico ---
            cursor.execute("""
                SELECT A.oraInizio, P.durataMinuti 
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                WHERE A.id_medico = ? AND A.data = ? AND A.stato != 'Annullato' AND A.id != ?
            """, (idMedico, data_str, idAppuntamento))
            
            appuntamenti_medico = cursor.fetchall()
            for app in appuntamenti_medico:
                fine_es_str = Appuntamento.calcolaOraFine(app['oraInizio'], app['durataMinuti'])
                
                if ora_str < fine_es_str and fine_nuovo_str > app['oraInizio']:
                    conn.close()
                    return False, f"Conflitto Medico: Il dottore è già occupato dalle {app['oraInizio']} alle {fine_es_str}."

            # --- FASE 2b: Verifica Conflitti nell'Agenda del Paziente ---
            cursor.execute("""
                SELECT A.oraInizio, P.durataMinuti, M.cognome AS cognome_medico
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                JOIN Dipendente M ON A.id_medico = M.id
                WHERE A.cf_paziente = ? AND A.data = ? AND A.stato != 'Annullato' AND A.id != ?
            """, (cfPaziente, data_str, idAppuntamento))
            
            appuntamenti_paziente = cursor.fetchall()
            for app in appuntamenti_paziente:
                fine_es_str = Appuntamento.calcolaOraFine(app['oraInizio'], app['durataMinuti'])
                
                if ora_str < fine_es_str and fine_nuovo_str > app['oraInizio']:
                    conn.close()
                    return False, f"Conflitto Paziente: Ha già una visita (Dott. {app['cognome_medico']}) dalle {app['oraInizio']} alle {fine_es_str}."
            
            # --- FASE 3: Aggiornamento ---
            cursor.execute("UPDATE Appuntamento SET data = ?, oraInizio = ? WHERE id = ?", 
                           (data_str, ora_str, idAppuntamento))
            
            conn.commit()
            conn.close()
            return True, f"Appuntamento riprogrammato con successo alle {ora_str}."
            
        except sqlite3.Error as e:
            print(f"Errore modifica appuntamento: {e}")
            return False, "Errore generico del database durante la modifica."
        
    def getAgendaMedico(self, idMedico: int, data: date) -> list:
        """Restituisce gli appuntamenti di un medico per una specifica data."""
        
        # Conversione ESPLICITA: da oggetto date a stringa per il database
        data_str = data.isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Passiamo la stringa data_str alla query SQL
        query = """
            SELECT 
                A.id AS id_appuntamento, 
                A.oraInizio, 
                A.stato,
                A.oraInizio, 
                A.stato, 
                P.nome AS nome_paziente, 
                P.cognome AS cognome_paziente,
                P.cf AS cf_paziente,
                Pr.nomePrestazione
            FROM Appuntamento A
            JOIN Paziente P ON A.cf_paziente = P.cf
            JOIN Prestazione Pr ON A.id_prestazione = Pr.id
            WHERE A.id_medico = ? AND A.data = ?
            ORDER BY A.oraInizio ASC
        """
        
        cursor.execute(query, (idMedico, data_str))
        rows = cursor.fetchall()
        conn.close()
        
        # Per ora restituiamo una lista di dizionari comoda per la View
        agenda = [dict(row) for row in rows]
        return agenda
    
    def aggiungiPrestazione(self, nome: str, durata: int, costo: float) -> bool:
        """Inserisce una nuova prestazione nel catalogo (RF10)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO Prestazione (nomePrestazione, durataMinuti, costoBase) VALUES (?, ?, ?)",
                (nome, durata, costo)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Errore DB in aggiungiPrestazione: {e}")
            return False

    def registraValutazioneFunzionale(self, idAppuntamento: int, anomalie: str, noteAggiuntive: str, prevOvertraining: str, valutazioneClinica: int) -> bool:
        """
        Crea la valutazione funzionale e la collega all'appuntamento.
        (Rispetta esattamente i parametri stringa/int del tuo UML).
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 1. Inseriamo la nuova Valutazione
            cursor.execute('''
                INSERT INTO ValutazioneFunzionale (anomalie, noteAggiuntive, prevOvertraining, valutazioneClinica)
                VALUES (?, ?, ?, ?)
            ''', (anomalie, noteAggiuntive, prevOvertraining, valutazioneClinica))
            
            # Recuperiamo l'ID appena generato da SQLite
            id_nuova_valutazione = cursor.lastrowid
            
            # 2. Aggiorniamo l'appuntamento collegandogli questo ID
            cursor.execute("UPDATE Appuntamento SET id_valutazione = ?, stato = 'Completato' WHERE id = ?", 
                           (id_nuova_valutazione, idAppuntamento))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Errore registrazione valutazione: {e}")
            return False

    def inviaPromemoriaAutomatici(self) -> None:
        """
        Cerca gli appuntamenti di domani, crea il record in Memo e simula l'invio (RF16).
        Restituisce void (None in Python) come da UML.
        """
        domani = (date.today() + timedelta(days=1)).isoformat()
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 1. Usiamo la JOIN per estrarre anche i contatti del paziente
            query = """
                SELECT A.id, A.oraInizio, P.nome, P.cognome, P.email 
                FROM Appuntamento A
                JOIN Paziente P ON A.cf_paziente = P.cf
                WHERE A.data = ? AND A.stato = 'Programmato'
            """
            cursor.execute(query, (domani,))
            appuntamenti_domani = cursor.fetchall()

            print(f"\n--- [SISTEMA] Avvio invio promemoria per il {domani} ---")
            
            if not appuntamenti_domani:
                print("Nessun appuntamento in programma per domani.")
            
            for app in appuntamenti_domani:
                # 2. Generiamo il testo "al volo" solo per simulare l'email nel terminale
                testo_memo = f"Gentile {app['nome']} {app['cognome']}, le ricordiamo la visita di domani alle ore {app['oraInizio']}."
                
                # 3. Inseriamo il record in Memo RISPETTANDO IL TUO UML
                # Passiamo 'domani' come data programmata e '1' come stato (True = Inviato)
                cursor.execute(
                    "INSERT INTO Memo (dataInvioProgrammata, inviato) VALUES (?, ?)", 
                    (domani, 1)
                )
                id_nuovo_memo = cursor.lastrowid # Recuperiamo l'ID appena generato
                
                # 4. Colleghiamo il Memo all'Appuntamento
                cursor.execute(
                    "UPDATE Appuntamento SET id_memo = ? WHERE id = ?",
                    (id_nuovo_memo, app['id'])
                )
                
                # 5. Simulazione visiva dell'invio (Il DB non sa nulla di questo testo)
                print(f"-> Inviata Email a: {app['email']} | Testo: {testo_memo}")
            
            conn.commit()
            conn.close()
            print("------------------------------------------------------\n")
            
        except sqlite3.Error as e:
            print(f"Errore DB durante l'invio dei promemoria: {e}")
    
    def getStoricoPaziente(self, cf_paziente: str) -> list:
        """Recupera tutto lo storico delle visite di un paziente specifico."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                A.data, 
                Pr.nomePrestazione, 
                M.nome AS nome_medico, M.cognome AS cognome_medico,
                A.stato,
                A.id_valutazione
            FROM Appuntamento A
            JOIN Prestazione Pr ON A.id_prestazione = Pr.id
            JOIN Dipendente M ON A.id_medico = M.id
            WHERE A.cf_paziente = ?
            ORDER BY A.data DESC, A.oraInizio DESC
        """
        cursor.execute(query, (cf_paziente,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def getDettagliValutazione(self, id_valutazione: int) -> dict:
        """Recupera il testo del referto medico."""
        if not id_valutazione:
            return {}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT anomalie, noteAggiuntive, prevOvertraining, valutazioneClinica FROM ValutazioneFunzionale WHERE id = ?", (id_valutazione,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}