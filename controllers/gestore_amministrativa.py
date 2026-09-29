import sqlite3
from datetime import datetime
from typing import Optional

class GestoreAmministrativa:
    def __init__(self, db_path="database/clinica.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def getAppuntamentiDaSaldare(self, cf_paziente: str) -> list:
        """Recupera gli appuntamenti completati ma non ancora pagati."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Un appuntamento è da saldare se è "Completato" e non esiste in Pagamento
            # ovvero non c e' l'id dell appuntamento nella riga corrispondente
            query = """
                SELECT A.id, A.data, Pr.nomePrestazione, Pr.costoBase
                FROM Appuntamento A
                JOIN Prestazione Pr ON A.id_prestazione = Pr.id
                WHERE A.cf_paziente = ? AND A.stato = 'Completato'
                AND A.id NOT IN (SELECT appuntamento_id FROM Pagamento)
            """
            cursor.execute(query, (cf_paziente,))
            risultati = cursor.fetchall()
            #si ritorna la lista delle informazioni dei pagamenti
            return [dict(row) for row in risultati]
        finally:
            conn.close()
    
    def verificaSaldoAppuntamento(self, id_appuntamento: int) -> bool:
        """Verifica se un appuntamento è già stato pagato."""
        #risponde con vero o falso se  e' gia stato saldato
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Pagamento WHERE appuntamento_id = ?", (id_appuntamento,))
            #"Cerca nella tabella Pagamento e dimmi se esiste una riga 
            # il cui campo appuntamento_id corrisponde all'ID dell'appuntamento 
            # che ti sto passando
            pagato = cursor.fetchone() is not None #recupera la prima riga
            #e ritorna true se non e' nulla, ovvero c e' un ID
            return pagato
        finally:
            conn.close()

    def registraPagamento(self, id_appuntamento: int, importo: float, metodo: str) -> Optional[int]:
        """ Registra il pagamento nel database."""
        if self.verificaSaldoAppuntamento(id_appuntamento):
            return None # Già pagato!

        data_ora_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                #se non e' gia pagato lo inserisco nel DB con le informazioni
                cursor.execute(
                    "INSERT INTO Pagamento (appuntamento_id, dataOraPagamento, importo, metodo) VALUES (?, ?, ?, ?)",
                    (id_appuntamento, data_ora_attuale, importo, metodo)
                )
                id_nuovo_pagamento = cursor.lastrowid
                conn.commit()
                #ritorno l'id come controllo e per poi passarlo alla fattura
                return id_nuovo_pagamento
            finally:
                conn.close()
        except sqlite3.Error as e:
            print(f"Errore DB in registraPagamento: {e}")
            return None

    def emettiFattura(self, id_pagamento: int, metodo_emissione: str) -> bool:
        """
        Genera il documento fiscale e ne simula l'emissione.
        metodo_emissione può essere 'Stampa' o 'Email'.
        """
        # 1. Recupero i dati del pagamento e del paziente per compilare la fattura
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Una JOIN per prendere tutti i dati necessari alla fattura, del paziente e pagamento
            query_dati = """
                SELECT P.importo, Paz.cf, Paz.nome, Paz.cognome, Paz.email
                FROM Pagamento P
                JOIN Appuntamento A ON P.appuntamento_id = A.id
                JOIN Paziente Paz ON A.cf_paziente = Paz.cf
                WHERE P.id = ?
            """
            cursor.execute(query_dati, (id_pagamento,))
            dati = cursor.fetchone()
            
            if not dati:
                return False

            # 2. Generazione Numero Fattura univoco (es. FATT-2026-001)
            numero_fattura = f"FATT-{datetime.now().year}-{id_pagamento:04d}"
            data_ora_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 3. Salvataggio della Fattura nel Database, usando i dati ricavati prima
            try:
                cursor.execute(
                    "INSERT INTO Fattura (pagamento_id, cf_paziente, numeroFattura, dataOraEmissione, totale) VALUES (?, ?, ?, ?, ?)",
                    (id_pagamento, dati['cf'], numero_fattura, data_ora_attuale, dati['importo'])
                )
                conn.commit()
                
                # 4. Simulazione Emissione
                print(f"\n--- [SISTEMA] EMISSIONE FATTURA {numero_fattura} ---")
                print(f"Paziente: {dati['nome']} {dati['cognome']} ({dati['cf']})")
                print(f"Totale: {dati['importo']}€")
                
                if metodo_emissione == 'Email':
                    print(f"-> Fattura inviata in formato PDF all'indirizzo: {dati['email']}")
                else:
                    print("-> Fattura inviata alla stampante della Segreteria.")
                print("----------------------------------------------------\n")
                
                return True
                
            except sqlite3.Error as e:
                print(f"Errore DB in emettiFattura: {e}")
                return False
        finally:
            conn.close()

    def getStoricoFatturePaziente(self, cf_paziente: str) -> list:
        """Recupera tutte le fatture emesse per un paziente."""
        #recuperra dalla tabella Fattura i dati filtrando per CF e ordinando
        #in moodo decrescente
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT numeroFattura, dataOraEmissione, totale FROM Fattura WHERE cf_paziente = ? ORDER BY dataOraEmissione DESC",
                (cf_paziente,)
            )
            risultati = cursor.fetchall()
            return [dict(row) for row in risultati]
        finally:
            conn.close()