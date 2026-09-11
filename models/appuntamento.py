from models.paziente import Paziente
from models.dipendente import Medico
from models.prestazione import Prestazione 
from models.memo import Memo
from models.valutazione_funzionale import ValutazioneFunzionale
from datetime import datetime, timedelta

class Appuntamento:
    """ Classe centrale del progetto: collega Paziente, Medico, Prestazione,
    e opzionalmente Memo/ValutazioneFunzionale (che infatti nascono a None,
    perché all'inizio un appuntamento non ha ancora un promemoria inviato
    né un referto — vengono "riempiti" più avanti nel ciclo di vita)."""
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
        #calcola ora fine sommando la durata all ora di inizio
        formato = "%H:%M" #dal formato capisce qual e' l ora e quale i minuti
        #converte un testo in oggetto per farci calcoli per poi ritrasformarlo in testo
        ora_inizio_obj = datetime.strptime(ora_inizio, formato)
        #timedelta serve a dire che quell intero passato sono i minuti
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
            "paziente": self.__paziente, 
            "medico": self.__medico,    
            "prestazione": self.__prestazione,
            "stato": self.__stato,
            "memo": self.__memo,
            "valutazioneFunzionale": self.__valutazioneFunzionale
        }
        
    def getPaziente(self) -> Paziente:
        return self.__paziente
    
    def getPrestazione(self) -> Prestazione:
        return self.__prestazione

    # --- Setters per la parte clinica ---
    
    def setMemo(self, nuovo_memo: Memo) -> None:
        self.__memo = nuovo_memo
        
    def setValutazioniFunzionali(self, nuova_valutazione: ValutazioneFunzionale) -> None:
        self.__valutazioneFunzionale = nuova_valutazione

    def setStato(self, nuovo_stato: str) -> None:
        self.__stato = nuovo_stato