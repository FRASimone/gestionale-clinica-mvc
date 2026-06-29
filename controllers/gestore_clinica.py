import sqlite3
from datetime import date, timedelta

# Importiamo i models che abbiamo appena costruito
from models.prestazione import Prestazione
from models.cartella_clinica import CartellaClinica

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

# ... (resto del codice) ...

    def creaAppuntamento(self, data: date, ora: time, cfPaziente: str, idMedico: int, idPrestazione: int) -> bool:
        # Il Controller traduce gli oggetti Date e Time in stringhe per SQLite ("YYYY-MM-DD" e "HH:MM")
        data_str = data.isoformat()
        ora_str = ora.strftime("%H:%M")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Appuntamento 
                (data, oraInizio, stato, cf_paziente, id_medico, id_prestazione, id_memo, id_valutazione) 
                VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            ''', (data_str, ora_str, "Programmato", cfPaziente, idMedico, idPrestazione))
            
            conn.commit()
            conn.close()
            return True, "Appuntamento prenotato con successo."
            
        except sqlite3.Error as e:
            print(f"Errore creazione appuntamento: {e}")
            return False
        
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

    def modificaOrarioAppuntamento(self, idAppuntamento: int, nuovaData: date, nuovaOra: time) -> bool:
        """Aggiorna data e ora di un appuntamento esistente."""
        
        # Conversione ESPLICITA: da oggetti Python a stringhe per il database
        data_str = nuovaData.isoformat()
        ora_str = nuovaOra.strftime("%H:%M")
        #Aggiorna dati e ora di un appuntamento esistente
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Passiamo le stringhe tradotte (data_str, ora_str) alla query
            cursor.execute("UPDATE Appuntamento SET data = ?, oraInizio = ? WHERE id = ?", 
                           (data_str, ora_str, idAppuntamento))
            
            conn.commit()
            righe_modificate = cursor.rowcount
            conn.close()
            return righe_modificate > 0
        except sqlite3.Error:
            return False

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
        Cerca gli appuntamenti di domani e simula l'invio del Memo.
        Restituisce void (None in Python) come da UML.
        """
        domani = (date.today() + timedelta(days=1)).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Appuntamento WHERE data = ? AND stato = 'Programmato'", (domani,))
        appuntamenti_domani = cursor.fetchall()
        conn.close()

        print(f"\n--- [SISTEMA] Avvio invio promemoria per il {domani} ---")
        for app in appuntamenti_domani:
            print(f"-> Inviato Memo per appuntamento ID: {app['id']} (Paziente: {app['cf_paziente']})")
        print("------------------------------------------------------\n")
    
    def getStoricoPaziente(self, cf_paziente: str) -> list:
        """Recupera tutto lo storico delle visite di un paziente specifico (RF8)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                A.data, 
                Pr.nomePrestazione, 
                M.nome AS nome_medico, M.cognome AS cognome_medico,
                A.stato
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
