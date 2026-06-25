from models.paziente import Paziente
from models.dipendente import Medico
from models.prestazione import Prestazione 
from models.memo import Memo
from models.valutazione_funzionale import ValutazioneFunzionale

class Appuntamento:
    def __init__(self, id_appuntamento: int, data: str, oraInizio: str, stato: str, 
                 paziente: Paziente, medico: Medico, prestazione: Prestazione, 
                 memo: Memo = None, valutazione: ValutazioneFunzionale = None):
        
        self.__id = id_appuntamento
        self.__data = data
        self.__oraInizio = oraInizio
        self.__stato = stato
        self.__paziente = paziente
        self.__medico = medico
        self.__prestazione = prestazione
        
        # Inizializzati a None, verranno riempiti se/quando generati
        self.__memo = memo
        self.__valutazione = valutazione

    # --- Metodi di Logica ---
    
    def calcolaOraFine(self, durata_minuti: int) -> str:
        """
        Prende l'ora di inizio, aggiunge i minuti di durata e restituisce l'ora di fine.
        Risolve automaticamente i riporti (es. 10:45 + 30 min = 11:15).
        """
        # Trasforma la stringa "HH:MM" in un oggetto tempo di Python
        formato = "%H:%M"
        ora_inizio_obj = datetime.strptime(self.__oraInizio, formato)
        
        # Aggiunge i minuti indicati nell'intero
        ora_fine_obj = ora_inizio_obj + timedelta(minutes=durata_minuti)
        
        # Ritrasforma l'oggetto tempo in una stringa "HH:MM"
        return ora_fine_obj.strftime(formato)

    # --- Getters ---
    
    def getId(self) -> int:
        return self.__id

    def getDettagli(self) -> dict:
        """Rispetta il nome e la struttura della tua progettazione."""
        return {
            "id": self.__id,
            "data": self.__data,
            "oraInizio": self.__oraInizio,
            "paziente": self.__paziente, # Restituisce l'oggetto
            "medico": self.__medico,     # Restituisce l'oggetto
            "stato": self.__stato,
            "memo": self.__memo,
            "valutazioniFunzionali": self.__valutazioniFunzionali
        }

    # --- Setters per la parte clinica ---
    
    def setMemo(self, nuovo_memo: str) -> None:
        self.__memo = nuovo_memo
        
    def setValutazioniFunzionali(self, nuove_valutazioni: str) -> None:
        self.__valutazioniFunzionali = nuove_valutazioni

    def setStato(self, nuovo_stato: str) -> None:
        self.__stato = nuovo_stato