import sqlite3
import random

# Importiamo i Model appena creati
from models.dipendente import Medico, Segretario, Amministratore
from models.paziente import Paziente
from typing import List
import re

class GestoreAnagrafica:
    def __init__(self, db_path="database/clinica.db"):
        self.db_path = db_path

    def _get_connection(self):
        """Metodo di supporto per connettersi velocemente al DB."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permette di accedere alle colonne per nome
        return conn

    def registraDipendente(self, nome, cognome, email, password, ruolo):
        """Registra un nuovo dipendente."""
        # controllo password sulla lunghezza
        if len(password) < 8:
            return False, "Errore: La password deve contenere almeno 8 caratteri."
        # controllo che nella password ci siano sia numeri che lettere
        if not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            return False, "Errore: La password deve contenere almeno una lettera e un numero."

        # Simulazione invio codice OTP per verifica email
        codice_verifica = random.randint(100000, 999999)
        print(f"\n--- [SIMULAZIONE] EMAIL INVIATA A: {email} ---")
        print(f"Oggetto: Codice di verifica Registrazione Clinica")
        print(f"Messaggio: Il tuo codice di verifica è {codice_verifica}")
        print("--------------------------------------------------\n")

        # In un progetto reale qui bloccheremmo il salvataggio in attesa del codice.
        # Per mantenere l'UI semplice, lo salviamo direttamente ma dimostriamo 
        # che la logica di verifica è predisposta.
        try:
            # chiamata al metodo di connessione
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                #la libreria sqlite3 è programmata per cercare i ? all'interno della stringa SQL.
                # inoltre evita SQL Injection 
                cursor.execute(
                    "INSERT INTO Dipendente (nome, cognome, email, password, ruolo) VALUES (?, ?, ?, ?, ?)",
                    (nome, cognome, email, password, ruolo)
                )
                conn.commit() # conferma finale
                return True, f"Registrazione completata. (Codice inviato: {codice_verifica})"
            finally:
                conn.close() # chiusura connessione
        except sqlite3.IntegrityError: #errore di unicita'
            return False, "Errore: Questa email è già presente nel sistema."
        except Exception as e:
            return False, f"Errore del database: {str(e)}"
    
    def modifica_ruolo(self, id_dipendente: int, nuovo_ruolo: str) -> bool:
        """Aggiorna il ruolo di un dipendente nel database."""
        #dall'id modifica il ruolo corrispondente nel nuovo passato
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
    
                cursor.execute("SELECT ruolo FROM Dipendente WHERE id = ?", (id_dipendente,))
                row = cursor.fetchone()
                if not row:
                    return False
                ruolo_attuale = row["ruolo"]
    
                cursor.execute(
                    "UPDATE Dipendente SET ruolo = ? WHERE id = ?",
                    (nuovo_ruolo, id_dipendente)
                )
                righe_aggiornate = cursor.rowcount   # <-- catturato SUBITO dopo la UPDATE
                #serve a vedere se il cambio e' andato a buon fine
    
                if ruolo_attuale == "Medico" and nuovo_ruolo != "Medico":
                    cursor.execute(
                        "DELETE FROM Medico_Specializzazione WHERE id_medico = ?",
                        (id_dipendente,)
                    )
    
                conn.commit()
                return righe_aggiornate > 0
            finally:
                conn.close()
        except Exception as e:
            print(f"Errore aggiornamento ruolo: {e}")
            return False
        
    def get_tutti_dipendenti(self) -> list:
        """Recupera la lista di tutti i dipendenti per la schermata di Gestione Ruoli."""
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                #recupera le informazioni dei dipendenti dalla tabella Dipendente
                cursor.execute("SELECT id, nome, cognome, email, ruolo FROM Dipendente")
                rows = cursor.fetchall()
            finally:
                conn.close()
            
            risultati = []
            for row in rows:
                risultati.append({
                    "id": row["id"],
                    "nome": row["nome"],
                    "cognome": row["cognome"],
                    "email": row["email"],
                    "ruolo": row["ruolo"]
                })
            return risultati
        except Exception as e:
            print(f"Errore DB in get_tutti_dipendenti: {e}")
            return []
    
    def assegnaSpecializzazione(self, idMedico: int, idSpecializzazione: int) -> bool:
        """
        Associa una specializzazione a un medico esistente nel database.
        Riflette la relazione Molti-a-Molti dell'UML.
        """
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                
                # Inseriamo il collegamento nella tabella ponte
                cursor.execute(
                    "INSERT INTO Medico_Specializzazione (id_medico, id_specializzazione) VALUES (?, ?)",
                    (idMedico, idSpecializzazione)
                )
                conn.commit()
            finally:
                conn.close()
            
            print(f"--- [SISTEMA] Specializzazione {idSpecializzazione} assegnata al Medico {idMedico} ---")
            return True
            
        except sqlite3.IntegrityError:
            # Scatta se proviamo ad assegnare la stessa specializzazione due volte allo stesso medico
            print("Avviso: Il medico possiede già questa specializzazione.")
            return False
        except Exception as e:
            print(f"Errore DB in assegnaSpecializzazione: {e}")
            return False

    def cercaUtentePerEmail(self, email: str):
        """Passo 1 del diagramma: ricercaUtente(email)."""
        # metodo che si connette al database recupera tutte le informazioni
        # relative all'email e ritorna il primo risultato (unico)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Dipendente WHERE email = ?", (email,))
            row = cursor.fetchone()
        finally:
            conn.close()
        return dict(row) if row else None

    def login(self, email, password, ruolo):
        # chiama il metodo per trovare le informazioni
        dati_utente = self.cercaUtentePerEmail(email)
        # controlla l'esistenza dell'utente nel database
        if dati_utente is None:
            return None, "utente_inesistente"

        # Passo 2 del diagramma: verificaCredenziali() come logica separata
        if dati_utente["password"] != password or dati_utente["ruolo"] != ruolo:
            return None, "credenziali_errate"
        # creazione dell'oggetto
        if ruolo == "Medico":
            oggetto = Medico(dati_utente['id'], dati_utente['nome'], dati_utente['cognome'], dati_utente['email'], dati_utente['password'])
        elif ruolo == "Segretario":
            oggetto = Segretario(dati_utente['id'], dati_utente['nome'], dati_utente['cognome'], dati_utente['email'], dati_utente['password'])
        elif ruolo == "Amministratore":
            oggetto = Amministratore(dati_utente['id'], dati_utente['nome'], dati_utente['cognome'], dati_utente['email'], dati_utente['password'])

        return oggetto, "ok"

    def recuperaCredenziali(self, email):
        """Implementa il Requisito: Recupero credenziali tramite email.
        """
        #si connette al database e prende la password corrispondente all'email passata
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM Dipendente WHERE email = ?", (email,))
            row = cursor.fetchone()
        finally:
            conn.close()

        if row:
            # Se troviamo l'email nel database: simuliamo l'invio dell'email con password
            password_recuperata = row['password']
            print(f"\n--- [SIMULAZIONE] EMAIL INVIATA A: {email} ---")
            print(f"Oggetto: Recupero credenziali Gestionale Clinica")
            print(f"Messaggio: La tua password è: {password_recuperata}")
            print("--------------------------------------------------\n")
            return True, "Ti abbiamo inviato un'email con le tue credenziali."
        
        return False, "Non esiste nessun dipendente registrato con questa email."
    
    def aggiungiPaziente(self, cf, nome, cognome, email, telefono, is_agonista):
        """Inserisce un nuovo paziente nel database."""
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    #aggiungiamo nel database
                    "INSERT INTO Paziente (cf, nome, cognome, email, telefono, isAgonista) VALUES (?, ?, ?, ?, ?, ?)",
                    (cf, nome, cognome, email, telefono, int(is_agonista)) # SQLite salva i boolean come 0 o 1
                )
                conn.commit()
            finally:
                conn.close()
            # Se va a buon fine, restituisce l'oggetto Paziente
            return Paziente(cf, nome, cognome, email, telefono, is_agonista)
        except sqlite3.IntegrityError:
            return None # Il Codice Fiscale esiste già, il CF e' unico
        except Exception as e:
            print(f"Errore DB in aggiungiPaziente: {e}")
            return None

    def ricercaPaziente(self, parametro_ricerca: str) -> List[Paziente]:
        """Cerca un paziente per Codice Fiscale o per Cognome."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                #prendiamo tutto dalla tabella paziente se il CF corrisponde
                #precisamente o il cognome e' simile
                "SELECT * FROM Paziente WHERE cf = ? OR cognome LIKE ?",
                (parametro_ricerca, f"%{parametro_ricerca}%")
            )
            rows = cursor.fetchall()
        finally:
            conn.close()
        
        risultati = []
        for row in rows:
            #creiamo gli oggetti paziente per ogni riga
            paz = Paziente(row['cf'], row['nome'], row['cognome'], row['email'], row['telefono'], bool(row['isAgonista']))
            risultati.append(paz)
        
        return risultati # Restituisce una lista di oggetti Paziente

    def modificaSchedaPaziente(self, cf, nuovi_dati: dict):
        """Aggiorna i contatti e lo stato agonistico di un paziente esistente."""
        #controllo sulla presenza delle chiavi presenti e non sui valori
        #serve ad evitare un crash da parte della query
        if "email" not in nuovi_dati or "telefono" not in nuovi_dati or "isAgonista" not in nuovi_dati:
            return False
            
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    #modifico la riga del Paziente collegato al CF passato con i dati nuovi
                    "UPDATE Paziente SET email = ?, telefono = ?, isAgonista = ? WHERE cf = ?",
                    (nuovi_dati["email"], nuovi_dati["telefono"], int(nuovi_dati["isAgonista"]), cf)
                )
                conn.commit()
                righe_aggiornate = cursor.rowcount
            finally:
                conn.close()
            return righe_aggiornate > 0
        except Exception as e:
            print(f"Errore DB in modificaScheda: {e}")
            return False
    
    def getTutteSpecializzazioni(self) -> list:
        """Recupera tutte le specializzazioni dal DB per popolare la UI."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            #recuper l'id e il nome di tutte le specializzazioni
            cursor.execute("SELECT id, nome FROM Specializzazione")
            rows = cursor.fetchall()
        finally:
            conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    def getDipendenteByEmail(self, email: str) -> int:
        """Recupera l'ID di un dipendente appena registrato tramite la sua email."""
        # questo metodo sarebbe sostituibile con il cercaUtente restituendo solo l'id
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # seleziona solo l'id dove l'email e' uguale a quella passata
            cursor.execute("SELECT id FROM Dipendente WHERE email = ?", (email,))
            row = cursor.fetchone() # ritorna il primo risultato trovato, che sara' unico (email e' unica)
        finally:
            conn.close()
        # ritorna l'id se row contiene qualcosa, altrimenti non esiste
        return row["id"] if row else -1