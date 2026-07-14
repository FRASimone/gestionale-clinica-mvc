from datetime import datetime

class Memo:
    def __init__(self, id_memo: int, dataInvioProgrammata: datetime, inviato: bool = False):
        self.__id = id_memo
        self.__dataInvioProgrammata = dataInvioProgrammata
        self.__inviato = inviato

    def segnaComeInviato(self) -> None:
        """Cambia lo stato del memo in inviato."""
        self.__inviato = True

    # --- Getters ---
    
    def getDataInvioProgrammata(self) -> datetime:
        return self.__dataInvioProgrammata
    
    def getId(self) -> int:
        return self.__id

    def isInviato(self) -> bool:
        return self.__inviato