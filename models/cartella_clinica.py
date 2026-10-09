from datetime import date
from models.valutazione_funzionale import ValutazioneFunzionale

class CartellaClinica:
    """"Rappresenta il fascicolo clinico di un paziente: anamnesi generica più
    la lista delle valutazioni funzionali (referti) associate nel tempo."""
    def __init__(self, id_cartella: int, dataCreazione: date, anamnesiGenerica: str):
        self.__id = id_cartella
        self.__dataCreazione = dataCreazione
        self.__anamnesiGenerica = anamnesiGenerica

    def aggiornaAnamnesi(self, nuova_anamnesi: str) -> None:
        self.__anamnesiGenerica = nuova_anamnesi

    def getId(self) -> int:
        return self.__id

    def getDataCreazione(self) -> date:
        return self.__dataCreazione

    def getAnamnesiGenerica(self) -> str:
        return self.__anamnesiGenerica