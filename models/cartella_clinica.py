from datetime import date
from models.valutazione_funzionale import ValutazioneFunzionale

class CartellaClinica:
    """"Rappresenta il fascicolo clinico di un paziente: anamnesi generica più
    la lista delle valutazioni funzionali (referti) associate nel tempo."""
    def __init__(self, id_cartella: int, dataCreazione: date, anamnesiGenerica: str):
        self.__id = id_cartella
        self.__dataCreazione = dataCreazione
        self.__anamnesiGenerica = anamnesiGenerica
        self.__valutazioni = [] # Inizializza una lista vuota

    def aggiornaAnamnesi(self, nuova_anamnesi: str) -> None:
        self.__anamnesiGenerica = nuova_anamnesi

    def aggiungiValutazione(self, valutazione: ValutazioneFunzionale) -> None:
        """Aggiunge un oggetto ValutazioneFunzionale alla lista della cartella."""
        self.__valutazioni.append(valutazione)

    # --- Getters ---
    def getValutazioni(self) -> list:
        return self.__valutazioni

    def getId(self) -> int:
        return self.__id

    def getDataCreazione(self) -> date:
        return self.__dataCreazione

    def getAnamnesiGenerica(self) -> str:
        return self.__anamnesiGenerica