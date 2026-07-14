from models.paziente import Paziente
from models.dipendente import Medico
from models.prestazione import Prestazione 
from models.memo import Memo
from models.valutazione_funzionale import ValutazioneFunzionale
from datetime import datetime, timedelta

class Appuntamento:
    def __init__(self, id_appuntamento: int, data: str, oraInizio: str, stato: str, 
                 paziente: Paziente, medico: Medico, prestazione: Prestazione, 
                 memo: Memo = None, valutazioneFunzionale: ValutazioneFunzionale = None):
        
        self.__id = id_appuntamento
        self.__data = data
        self.__oraInizio = oraInizio
        self.__stato = stato
        self.__paziente = paziente
        self.__medico = medico
        self.__prestazione = prestazione
        
        # Inizializzati a None, verranno riempiti se/quando generati
        self.__memo = memo
        self.__valutazioneFunzionale = valutazioneFunzionale

    # --- Metodi di Logica ---
    # --- Metodi di Logica ---
    
    @staticmethod
    def calcolaOraFine(ora_inizio: str, durata_minuti: int) -> str:
        """
        Metodo statico: calcola l'ora di fine senza dover istanziare l'oggetto.
        """
        formato = "%H:%M"
        ora_inizio_obj = datetime.strptime(ora_inizio, formato)
        ora_fine_obj = ora_inizio_obj + timedelta(minutes=durata_minuti)
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
            "prestazione": self.__prestazione,
            "stato": self.__stato,
            "memo": self.__memo,
            "valutazioneFunzionale": self.__valutazioneFunzionale
        }

    # --- Setters per la parte clinica ---
    
    def setMemo(self, nuovo_memo: Memo) -> None:
        self.__memo = nuovo_memo
        
    def setValutazioniFunzionali(self, nuova_valutazione: ValutazioneFunzionale) -> None:
        self.__valutazioneFunzionale = nuova_valutazione

    def setStato(self, nuovo_stato: str) -> None:
        self.__stato = nuovo_stato