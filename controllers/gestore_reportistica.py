import sqlite3
import json
from typing import Optional
from models.report import Report 

class GestoreReportistica:
    def __init__(self, db_path="database/clinica.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _salva_e_crea_oggetto(self, cursor, anno: int, mese: int, tipo: str, dati: dict) -> Report:
        """Utility privata: converte il dict in JSON, salva su DB e restituisce l'oggetto Model."""
        # json.dumps() converte il dizionario Python in una semplice stringa di testo
        # (formato JSON) in modo che possa essere salvato in una singola colonna del database.
        dati_json = json.dumps(dati)
        # Se mese è 0, significa che è un report annuale e passiamo None al DB
        # Se la UI richiede un report annuale, passa mese = 0.
        mese_db = mese if mese > 0 else None 

        #Inserimento del record nel database
        cursor.execute(
            "INSERT INTO Report (annoRiferimento, meseRiferimento, tipoReport, datiAggregati) VALUES (?, ?, ?, ?)",
            (anno, mese_db, tipo, dati_json)
        )
        #Recupero della chiave primaria autogenerata
        id_report = cursor.lastrowid
        #Creazione e restituzione dell'oggetto Model
        return Report(id=id_report, annoRiferimento=anno, meseRiferimento=mese_db, tipoReport=tipo, datiAggregati=dati)

    # --- METODI DI GENERAZIONE REPORT ---

    def generaReportPazienti(self, anno: int, mese: int = 0) -> Report:
        """RF20: Calcola il numero di pazienti visitati unici, ma anche numero visite (pazienti totali non unici) nel periodo."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Uso strftime per estrarre anno e mese dalla stringa ISO di SQLite
            # COUNT(id): conta il totale grezzo delle visite erogate.
            # COUNT(DISTINCT cf_paziente): conta quante persone fisiche diverse sono venute in clinica.
            query = """SELECT COUNT(id) AS visite, COUNT(DISTINCT cf_paziente) AS pazienti_unici
               FROM Appuntamento WHERE stato = 'Completato' AND strftime('%Y', data) = ?"""
            params = [str(anno)]
    
            # 3. Aggiunta del filtro mensile (se specificato nell'interfaccia)
            if mese > 0:
                query += " AND strftime('%m', data) = ?"
                params.append(f"{mese:02d}") # Formatta il mese con lo zero davanti (es. '05')
            # Esecuzione e recupero dei dati
            cursor.execute(query, params)
            # Estrae l'unica riga prodotta dai COUNT
            risultato = cursor.fetchone()
            
            dati = {"visite_completate": risultato['visite'],
            "pazienti_unici": risultato['pazienti_unici']}
            # Deleghiamo a un metodo di supporto il salvataggio su DB e la creazione dell'oggetto
            report = self._salva_e_crea_oggetto(cursor, anno, mese, "Pazienti", dati)
            
            conn.commit()
            return report
        finally:
            conn.close()

    def generaReportFatturatoGlobale(self, anno: int, mese: int = 0) -> Report:
        """RF20: Calcola il fatturato totale generato dalle fatture emesse."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = "SELECT SUM(totale) as incasso_totale FROM Fattura WHERE strftime('%Y', dataOraEmissione) = ?"
            params = [str(anno)]
            
            if mese > 0:
                query += " AND strftime('%m', dataOraEmissione) = ?"
                params.append(f"{mese:02d}")
    
            cursor.execute(query, params)
            risultato = cursor.fetchone()
            
            # Se non ci sono fatture, SUM restituisce None. Lo gestiamo forzando a 0.0
            totale = risultato['incasso_totale'] if risultato['incasso_totale'] else 0.0
            
            dati = {"fatturato_globale": totale}
            report = self._salva_e_crea_oggetto(cursor, anno, mese, "Fatturato Globale", dati)
            
            conn.commit()
            return report
        finally:
            conn.close()
    
    def generaReportFatturatoPrestazione(self, anno: int, mese: int = 0) -> Report:
        """RF21: Fatturato suddiviso per singola prestazione."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT Pr.nomePrestazione, SUM(F.totale) as totale_prestazione
                FROM Fattura F
                JOIN Pagamento P ON F.pagamento_id = P.id
                JOIN Appuntamento A ON P.appuntamento_id = A.id
                JOIN Prestazione Pr ON A.id_prestazione = Pr.id
                WHERE strftime('%Y', F.dataOraEmissione) = ?
            """
            params = [str(anno)]
            
            if mese > 0:
                query += " AND strftime('%m', F.dataOraEmissione) = ?"
                params.append(f"{mese:02d}")
                
            query += " GROUP BY Pr.id"
    
            cursor.execute(query, params)
            risultati = cursor.fetchall()
            
            dati = {row['nomePrestazione']: row['totale_prestazione'] for row in risultati}
            report = self._salva_e_crea_oggetto(cursor, anno, mese, "Fatturato Prestazione", dati)
            
            conn.commit()
            return report
        finally:
            conn.close()

    def generaReportFatturatoMedico(self, anno: int, mese: int = 0) -> Report:
        """RF22: Suddivide il fatturato in base al medico che ha erogato la prestazione."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT D.cognome, D.nome, SUM(F.totale) as totale_medico
                FROM Fattura F
                JOIN Pagamento P ON F.pagamento_id = P.id
                JOIN Appuntamento A ON P.appuntamento_id = A.id
                JOIN Dipendente D ON A.id_medico = D.id
                WHERE strftime('%Y', F.dataOraEmissione) = ?
            """
            params = [str(anno)]
            
            if mese > 0:
                query += " AND strftime('%m', F.dataOraEmissione) = ?"
                params.append(f"{mese:02d}")
                
            query += " GROUP BY D.id"
    
            cursor.execute(query, params)
            risultati = cursor.fetchall()
            
            dati = {}
            for row in risultati:
                chiave = f"Dr. {row['cognome']} {row['nome']}"
                dati[chiave] = row['totale_medico']
                
            report = self._salva_e_crea_oggetto(cursor, anno, mese, "Fatturato Medico", dati)
            
            conn.commit()
            return report
        finally:
            conn.close()
    
    def generaReportStatisticoPrestazioni(self, anno: int, mese: int = 0) -> Report:
        """RF23: Statistica (conteggio) delle prestazioni erogate."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT Pr.nomePrestazione, COUNT(A.id) as conteggio
                FROM Appuntamento A
                JOIN Prestazione Pr ON A.id_prestazione = Pr.id
                WHERE A.stato = 'Completato' AND strftime('%Y', A.data) = ?
            """
            params = [str(anno)]
            
            if mese > 0:
                query += " AND strftime('%m', A.data) = ?"
                params.append(f"{mese:02d}")
                
            query += " GROUP BY Pr.id"
    
            cursor.execute(query, params)
            risultati = cursor.fetchall()
            
            dati = {row['nomePrestazione']: row['conteggio'] for row in risultati}
            report = self._salva_e_crea_oggetto(cursor, anno, mese, "Statistico Prestazioni", dati)
            
            conn.commit()
            return report
        finally:
            conn.close()
    
    def generaReportMensiliAutomatici(self, anno: int, mese: int) -> bool:
        """
        Esegue la generazione batch di tutti i report per il periodo indicato.
        """
        try:
            self.generaReportPazienti(anno, mese)
            self.generaReportFatturatoGlobale(anno, mese)
            self.generaReportFatturatoPrestazione(anno, mese)
            self.generaReportFatturatoMedico(anno, mese)
            self.generaReportStatisticoPrestazioni(anno, mese)
            
            print(f"--- [SISTEMA] Generazione automatica report completata per {mese}/{anno} ---")
            return True
        except Exception as e:
            print(f"Errore durante la generazione batch dei report: {e}")
            return False

    # --- METODI DI VISUALIZZAZIONE ED ESPORTAZIONE ---

    def getListaReport(self, anno: int, mese: int, tipoReport: str) -> list:
        """RF25: Recupera e filtra la lista dei report."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Costruiamo la query dinamicamente in base ai filtri passati
            #'WHERE 1=1' è una condizione sempre vera che non filtra nulla di per sé.
            # È una base d'appoggio: permette di accodare dinamicamente i vari " AND ..." 
            # successivi senza doversi preoccupare di controllare ogni volta se 
            # la parola "WHERE" è già stata inserita o meno nella stringa SQL.
            query = "SELECT id, annoRiferimento, meseRiferimento, tipoReport FROM Report WHERE 1=1"
            params = []
            #ricaviamo i filtri selezionati in view e costruiamo la query
            if anno > 0:
                query += " AND annoRiferimento = ?"
                params.append(anno)
            if mese > 0:
                query += " AND meseRiferimento = ?"
                params.append(mese)
            if tipoReport != "Tutti":
                query += " AND tipoReport = ?"
                params.append(tipoReport)
            #chiamiamo la query con i vari parametri
            cursor.execute(query, params)
            risultati = cursor.fetchall()
            
            return [dict(row) for row in risultati]
        finally:
            conn.close()

    def visualizzaReport(self, id_report: int) -> Optional[dict]:
        """RF25: Recupera un report specifico e decodifica il JSON in dizionario."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Report WHERE id = ?", (id_report,))
            riga = cursor.fetchone()
            
            if riga:
                dati = dict(riga)
                # Riconvertiamo la stringa JSON nel dizionario Python originale
                dati['datiAggregati'] = json.loads(dati['datiAggregati'])
                return dati
            return None
        finally:
            conn.close()

    def esportaReport(self, id_report: int, formato: str) -> bool:
        """RF24: Simula l'esportazione di un report in PDF o Excel."""
        report = self.visualizzaReport(id_report)
        if not report:
            return False
            
        estensione = ".pdf" if formato == "PDF" else ".xlsx"
        nome_file = f"Report_{report['tipoReport'].replace(' ', '_')}_{report['annoRiferimento']}{estensione}"
        
        print(f"\n--- [SISTEMA] ESPORTAZIONE AVVIATA ---")
        print(f"-> Generazione file {nome_file} in corso...")
        print(f"-> Dati esportati: {report['datiAggregati']}")
        print(f"-> File salvato con successo nel file system aziendale.")
        print("----------------------------------------\n")
        
        return True