from datetime import datetime


class Fattura:
    def __init__(self, id_fattura: int, numeroFattura: str, dataOraEmissione: datetime,
                 totale: float, paziente=None):
        self.__id = id_fattura
        self.__numeroFattura = numeroFattura
        self.__dataOraEmissione = dataOraEmissione
        self.__totale = totale
        self.__paziente = paziente  # Oggetto Paziente intestatario (relazione "intestata a")

    # --- Getters ---

    def getId(self) -> int:
        return self.__id

    def getNumeroFattura(self) -> str:
        return self.__numeroFattura

    def getDataOraEmissione(self) -> datetime:
        return self.__dataOraEmissione

    def getTotale(self) -> float:
        return self.__totale

    def getPaziente(self):
        return self.__paziente

    def getDatiFiscale(self) -> dict:
        """Restituisce i dati fiscali impacchettati in un dizionario, pronto per la View."""
        return {
            "id": self.__id,
            "numeroFattura": self.__numeroFattura,
            "dataOraEmissione": self.__dataOraEmissione,
            "totale": self.__totale,
            "paziente": self.__paziente
        }