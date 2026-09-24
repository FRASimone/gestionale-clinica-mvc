import sqlite3
from datetime import date, timedelta, datetime, time 

# Importiamo i models che abbiamo appena costruito
from models.prestazione import Prestazione
from models.cartella_clinica import CartellaClinica
from models.appuntamento import Appuntamento

class AccessoNegatoError(Exception):
    pass


class GestoreClinica:
    def __init__(self, db_path="database/clinica.db"):
        self.db_path = db_path
        

    def _get_connection(self):
        """Metodo privato per la connessione al database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _verifica_ruolo(self, ruolo_utente: str, ruoli_ammessi: list):
        # _verifica_ruolo — si fida della stringa passata dalla UI
        #controllo quando prendo la cartellaClinica
        if ruolo_utente not in ruoli_ammessi:
            raise AccessoNegatoError(
                f"Operazione riservata a {ruoli_ammessi}, ruolo fornito '{ruolo_utente}'."
            )

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
        #qui a differenza dei due metodi sotto si lavora con i Model, incoerenza
        lista_prestazioni = []
        for row in rows:
            prestazione = Prestazione(row['id'], row['nomePrestazione'], row['durataMinuti'], row['costoBase'])
            lista_prestazioni.append(prestazione)
            
        return lista_prestazioni
    
    def getTuttiMedici(self) -> list:
        """Metodo di supporto per la View: recupera i medici per la tendina."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cognome FROM Dipendente WHERE ruolo = 'Medico'")
        #si prendono le informazioni di tutti i medici
        medici = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return medici
    
    def getTuttiPazienti(self) -> list:
        """Metodo di supporto per la View: recupera i pazienti per la tendina."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cf, nome, cognome FROM Paziente")
        #si prendono le informazioni di tutti i pazienti
        pazienti = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pazienti
    
    def aggiornaAnamnesi(self, cf_paziente: str, nuova_anamnesi: str, ruolo_utente="Medico") -> bool:
        """Crea o aggiorna l'anamnesi del paziente."""
        #verifica del ruolo lato controller
        self._verifica_ruolo(ruolo_utente, ["Medico"])
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            #si fa la select per verificare l'esistenza della riga CartellaClinica per quel CF
            cursor.execute("SELECT id FROM CartellaClinica WHERE cf_paziente = ?", (cf_paziente,))
            esiste = cursor.fetchone()
            #se l'anamnesi gia esiste la aggiorna
            if esiste:
                cursor.execute(
                    "UPDATE CartellaClinica SET anamnesiGenerica = ? WHERE cf_paziente = ?",
                    (nuova_anamnesi, cf_paziente)
                )
            else:
                #se non esiste viene creata
                cursor.execute(
                    "INSERT INTO CartellaClinica (anamnesiGenerica, dataCreazione, cf_paziente) VALUES (?, ?, ?)",
                    (nuova_anamnesi, date.today().isoformat(), cf_paziente)
                )

            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Errore aggiornamento anamnesi: {e}")
            return False
        
    def getCartellaClinica(self, cf_paziente: str, ruolo_utente="Medico") -> dict:
        """Recupera l'anamnesi del paziente."""
        #controllo lato controller del ruolo
        self._verifica_ruolo(ruolo_utente, ["Medico"]) #passiamo la lista di ruoli ammessi, ovvero solo il medico
        conn = self._get_connection()
        cursor = conn.cursor()
        #recupero la descrizione e la data dalla tabella al corrispettivo CF
        cursor.execute(
            "SELECT id, anamnesiGenerica, dataCreazione FROM CartellaClinica WHERE cf_paziente = ?",
            (cf_paziente,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    

    def creaAppuntamento(self, data: date, ora: time, cfPaziente: str, idMedico: int, idPrestazione: int) -> tuple:
        """Crea un appuntamento calcolando la durata e bloccando le sovrapposizioni."""
        data_str = data.isoformat() #prende la data e lo trasforma in testo
        ora_str = ora.strftime("%H:%M") #string format time
        if datetime.combine(data, ora) < datetime.now():
            return False, "Impossibile prenotare un appuntamento in un orario già passato."

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # --- FASE 1: Recupero durata e Calcolo Limiti ---
            # Dobbiamo prima fare la SELECT per definire "durata_nuova"
            cursor.execute("SELECT durataMinuti FROM Prestazione WHERE id = ?", (idPrestazione,))
            prestazione_nuova = cursor.fetchone()
            #controlla che esista l'id per la prestazione selezionata
            #anche se il controllo e' gia fatto dalla combo box perche mostra solo id validi
            if not prestazione_nuova:
                conn.close()
                return False, "Errore: Prestazione non trovata nel catalogo."
                
            durata_nuova = prestazione_nuova['durataMinuti']
            # Ora possiamo calcolare la fine usando il metodo statico
            fine_nuovo_str = Appuntamento.calcolaOraFine(ora_str, durata_nuova)
            
            # --- FASE 2a: Verifica Conflitti nell'Agenda del Medico ---
            cursor.execute("""
                SELECT A.oraInizio, P.durataMinuti 
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                WHERE A.id_medico = ? AND A.data = ? AND A.stato != 'Annullato'
            """, (idMedico, data_str))
            #la richiesta trova gli appuuntamenti fissati per il medico in quella giornata
            
            #prende la lista degli appuntamenti del medico
            appuntamenti_medico = cursor.fetchall()
            for app in appuntamenti_medico:
                #per ogni appuntamento calcola l'ora di fine
                fine_es_str = Appuntamento.calcolaOraFine(app['oraInizio'], app['durataMinuti'])
                #ce' un conflitto se il nuovo appuntamento inizia prima che finisca il vecchio
                #e se il nuovo appuntamento finisce dopo uno gia prenotato
                if ora_str < fine_es_str and fine_nuovo_str > app['oraInizio']:
                    conn.close()
                    return False, f"Conflitto Medico: Il dottore è già occupato dalle {app['oraInizio']} alle {fine_es_str}."

            # --- FASE 2b: Verifica Conflitti nell'Agenda del Paziente ---
            #stesso controllo ma lato paziente, per verificare che non abbia preso
            #due appuntamenti nella stessa fascia
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
            #infine viene inserito l'appuntamento
            cursor.execute('''
                INSERT INTO Appuntamento 
                (data, oraInizio, stato, cf_paziente, id_medico, id_prestazione, id_memo, id_valutazione) 
                VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            ''', (data_str, ora_str, "Programmato", cfPaziente, idMedico, idPrestazione))
            
            conn.commit()
            conn.close()
            return True, f"Appuntamento confermato.\n(Durata prevista: {durata_nuova} min. Fine: {fine_nuovo_str})"
            
        except sqlite3.Error as e:
            print(f"Errore creazione appuntamento: {e}")
            return False, "Errore generico del database durante la prenotazione."
    
    def annullaAppuntamento(self, idAppuntamento: int) -> bool:
            """Cambia lo stato dell'appuntamento in Annullato."""
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                #update per cambiare lo stato
                cursor.execute("UPDATE Appuntamento SET stato = 'Annullato' WHERE id = ?", (idAppuntamento,))
                conn.commit()
                righe_modificate = cursor.rowcount
                conn.close()
                return righe_modificate > 0
            except sqlite3.Error:
                return False
    
    def getDettagliAppuntamento(self, id_appuntamento: int) -> dict:
            """Recupera i dettagli di un singolo appuntamento per pre-compilare l'interfaccia di modifica."""
            conn = self._get_connection()
            cursor = conn.cursor()
            #recuperiamo la data l'ora e il paziente per mostrarlo nella view
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

    def modificaOrarioAppuntamento(self, idAppuntamento: int, nuovaData: date, nuovaOra: time) -> tuple:
        """Aggiorna data e ora di un appuntamento esistente, verificando prima i conflitti orari."""
        data_str = nuovaData.isoformat()
        ora_str = nuovaOra.strftime("%H:%M")
        if datetime.combine(nuovaData, nuovaOra) < datetime.now():
            return False, "Impossibile prenotare un appuntamento in un orario già passato."
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
             # --- FASE 0: Recupero dei dati attuali dell'appuntamento ---
            cursor.execute("""
                SELECT A.cf_paziente, A.id_medico, A.stato, A.data, A.oraInizio, A.id_memo, P.durataMinuti
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                WHERE A.id = ?
            """, (idAppuntamento,))
            app_corrente = cursor.fetchone()
            
            if not app_corrente:
                conn.close()
                return False, "Errore: Appuntamento non trovato nel sistema."

            # Verifica lato server: non si può modificare un appuntamento
            # già completato o annullato, a prescindere dai controlli fatti in UI
            if app_corrente['stato'] in ('Completato', 'Annullato'):
                conn.close()
                return False, f"Errore: impossibile modificare un appuntamento in stato '{app_corrente['stato']}'."
                
            cfPaziente = app_corrente['cf_paziente']
            idMedico = app_corrente['id_medico']
            durata_nuova = app_corrente['durataMinuti']
            
            # --- FASE 1: Calcolo Limiti del Nuovo Orario con i dati passati dalla view ---
            fine_nuovo_str = Appuntamento.calcolaOraFine(ora_str, durata_nuova)
            
            # --- FASE 2a: Verifica Conflitti nell'Agenda del Medico ---
            cursor.execute("""
                SELECT A.oraInizio, P.durataMinuti 
                FROM Appuntamento A
                JOIN Prestazione P ON A.id_prestazione = P.id
                WHERE A.id_medico = ? AND A.data = ? AND A.stato != 'Annullato' AND A.id != ?
            """, (idMedico, data_str, idAppuntamento))
            #logica uguale a crea Appuntamento ma qui nel where c e' un pezzo aggiuntivo
            # A.id != ? per escludere se stesso dal controllo
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
            #stessa logica di crea_Appuntamento, anche qui vale il discorso sopra
            appuntamenti_paziente = cursor.fetchall()
            for app in appuntamenti_paziente:
                fine_es_str = Appuntamento.calcolaOraFine(app['oraInizio'], app['durataMinuti'])
                
                if ora_str < fine_es_str and fine_nuovo_str > app['oraInizio']:
                    conn.close()
                    return False, f"Conflitto Paziente: Ha già una visita (Dott. {app['cognome_medico']}) dalle {app['oraInizio']} alle {fine_es_str}."
            
            # --- FASE 3: Aggiornamento ---
            vecchio_memo = app_corrente['id_memo']
            #a differenza della creazione qui al posto di insert si fa un update
            cursor.execute("UPDATE Appuntamento SET data = ?, oraInizio = ?, id_memo = NULL WHERE id = ?", 
                           (data_str, ora_str, idAppuntamento))
            if vecchio_memo:  # se l appuntamento aveva un memo viene eliminato
                cursor.execute("DELETE FROM Memo WHERE id = ?", (vecchio_memo,))
            
            conn.commit()
            conn.close()
            return True, f"Appuntamento riprogrammato con successo alle {ora_str}."
            
        except sqlite3.Error as e:
            print(f"Errore modifica appuntamento: {e}")
            return False, "Errore generico del database durante la modifica."
    
        
    def getAgendaMedico(self, idMedico: int, data: date) -> list:
        """Restituisce gli appuntamenti di un medico per una specifica data."""
        
        # Conversione: da oggetto date a stringa per il database
        data_str = data.isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        #cerchiamo gli appuntamenti del medico filtrati per id medico e data
        query = """
            SELECT 
                A.id AS id_appuntamento, 
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
        
        # restituiamo una lista di dizionari comoda per la View
        agenda = [dict(row) for row in rows]
        return agenda
    
    def aggiungiPrestazione(self, nome: str, durata: int, costo: float) -> bool:
        """Inserisce una nuova prestazione nel catalogo."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            #aggiungiamo la prestazione al DB
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
    
    def _verifica_ruolo_da_id(self, id_dipendente: int, ruoli_ammessi: list):
            """Verifica il ruolo REALE dell'utente consultando il database,
            invece di fidarsi di una stringa passata dalla UI."""
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT ruolo FROM Dipendente WHERE id = ?", (id_dipendente,))
            row = cursor.fetchone()
            conn.close()
    
            if not row or row['ruolo'] not in ruoli_ammessi:
                raise AccessoNegatoError(
                    f"Operazione riservata a {ruoli_ammessi}."
                )

    def registraValutazioneFunzionale(self, idAppuntamento: int, anomalie: str, noteAggiuntive: str,
                                   prevOvertraining: str, valutazioneClinica: int, id_medico: int) -> bool:
        """
        Crea la valutazione funzionale e la collega all'appuntamento.
        (Rispetta esattamente i parametri stringa/int del tuo UML).
        """
        # _verifica_ruolo_da_id — verifica il ruolo VERO leggendolo dal DB
        self._verifica_ruolo_da_id(id_medico, ["Medico"])
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Verifica lato server: l'appuntamento deve esistere ed essere ancora "Programmato".
            # Blocca la refertazione di appuntamenti Annullati o già Completati,
            # indipendentemente da eventuali controlli (bypassabili) fatti dalla UI.
            cursor.execute("SELECT stato FROM Appuntamento WHERE id = ?", (idAppuntamento,))
            riga_stato = cursor.fetchone()
            if not riga_stato or riga_stato['stato'] != 'Programmato':
                conn.close()
                return False
            
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

    def inviaPromemoriaAutomatici(self) -> int:
        """
        Cerca gli appuntamenti di domani, crea il record in Memo e simula l'invio."""
        #calcola la data di domani
        domani = (date.today() + timedelta(days=1)).isoformat()
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # selezioniamo le informazioni del paziente e gli appuntamenti che
            #sono nello stato programmato e che iniziano domani,
            #senza poter inviare due volte il memo
            query = """
                SELECT A.id, A.oraInizio, P.nome, P.cognome, P.email 
                FROM Appuntamento A
                JOIN Paziente P ON A.cf_paziente = P.cf
                WHERE A.data = ? AND A.stato = 'Programmato' AND A.id_memo IS NULL
            """
            cursor.execute(query, (domani,))
            appuntamenti_domani = cursor.fetchall()

            print(f"\n--- [SISTEMA] Avvio invio promemoria per il {domani} ---")
            
            if not appuntamenti_domani:
                print("Nessun appuntamento in programma per domani.")
            
            for app in appuntamenti_domani:
                # 2. Generiamo il testo solo per simulare l'email nel terminale
                testo_memo = f"Gentile {app['nome']} {app['cognome']}, le ricordiamo la visita di domani alle ore {app['oraInizio']}."
                
                # 3. Inseriamo il record in Memo
                # Passiamo 'domani' come data programmata e '1' come stato (True = Inviato)
                cursor.execute(
                    "INSERT INTO Memo (dataInvioProgrammata, inviato) VALUES (?, ?)", 
                    (domani, 1)
                )
                id_nuovo_memo = cursor.lastrowid # Recuperiamo l'ID appena generato
                
                # 4. Colleghiamo il Memo all'Appuntamento
                # serve a sapere se un appuntamento ha già ricevuto un promemoria.
                cursor.execute(
                    "UPDATE Appuntamento SET id_memo = ? WHERE id = ?",
                    (id_nuovo_memo, app['id'])
                )
                
                # 5. Simulazione visiva dell'invio
                print(f"-> Inviata Email a: {app['email']} | Testo: {testo_memo}")
            
            conn.commit()
            conn.close()
            print("------------------------------------------------------\n")
            return len(appuntamenti_domani)   # <-- conteggio di quanti sono stati notificati
            
        except sqlite3.Error as e:
            print(f"Errore DB durante l'invio dei promemoria: {e}")
            return -1
    
    def getStoricoPaziente(self, cf_paziente: str) -> list:
        """Recupera tutto lo storico delle visite di un paziente specifico."""
        conn = self._get_connection()
        cursor = conn.cursor()
        #dala tabella Appuntamento prende la data, lo stato e l'id della valutazione
        #dalla tabella Prestazione usando l'id recupera il nome
        #dalla tabella Dipendente usando l'id del medico ne prende il nome e cognome
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
        #"Prendi l'ID della prestazione salvato nell'appuntamento, 
        # cercalo nella tabella Prestazione e unisci i dati di quella riga". 
        # la query può accedere alla colonna nomePrestazione
        # stessa cosa per il medico
        #basandosi sul CF del paziente e ordinando i risultati in modo decrescente
        cursor.execute(query, (cf_paziente,))
        rows = cursor.fetchall()
        conn.close()
        #trasforma i risultati in una lista di dizionari
        return [dict(row) for row in rows]

    def getDettagliValutazione(self, id_valutazione: int, ruolo_utente="Medico") -> dict:
        """Recupera il testo del referto medico."""
        self._verifica_ruolo(ruolo_utente, ["Medico"])
        if not id_valutazione:
            return {}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT anomalie, noteAggiuntive, prevOvertraining, valutazioneClinica FROM ValutazioneFunzionale WHERE id = ?", (id_valutazione,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}
