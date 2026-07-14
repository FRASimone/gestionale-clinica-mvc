from datetime import datetime


class Pagamento:
    def __init__(self, id_pagamento: int, dataOraPagamento: datetime, importo: float,
                 metodo: str, appuntamento=None, fattura=None):
        self.__id = id_pagamento
        self.__dataOraPagamento = dataOraPagamento
        self.__importo = importo
        self.__metodo = metodo

        # Relazioni con altri oggetti (0..1 / 1, come da diagramma)
        self.__appuntamento = appuntamento   # Oggetto Appuntamento saldato
        self.__fattura = fattura             # Oggetto Fattura generata (può essere None finché non emessa)

    # --- Setter per collegare gli oggetti correlati dopo la creazione ---

    def setFattura(self, nuova_fattura) -> None:
        """Collega la Fattura generata a partire da questo pagamento."""
        self.__fattura = nuova_fattura

    def setAppuntamento(self, appuntamento) -> None:
        self.__appuntamento = appuntamento

    # --- Getters ---

    def getId(self) -> int:
        return self.__id

    def getImporto(self) -> float:
        return self.__importo

    def getMetodo(self) -> str:
        return self.__metodo

    def getDataOraPagamento(self) -> datetime:
        return self.__dataOraPagamento

    def getAppuntamento(self):
        return self.__appuntamento

    def getFattura(self):
        return self.__fattura

    def getDettagliTransazione(self) -> dict:
        """Restituisce i dati impacchettati in un dizionario, pronto per la View."""
        return {
            "id": self.__id,
            "dataOraPagamento": self.__dataOraPagamento,
            "importo": self.__importo,
            "metodo": self.__metodo,
            "appuntamento": self.__appuntamento,
            "fattura": self.__fattura
        }