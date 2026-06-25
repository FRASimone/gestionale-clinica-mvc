class Prestazione:
    def __init__(self, id_prestazione: int, nomePrestazione: str, durataMinuti: int, costoBase: float):
        self.__id = id_prestazione
        self.__nomePrestazione = nomePrestazione
        self.__durataMinuti = durataMinuti
        self.__costoBase = costoBase

    def getCosto(self) -> float:
        return self.__costoBase

    def getDurata(self) -> int:
        return self.__durataMinuti

    def getInfoPrestazione(self) -> dict:
        return {
            "id": self.__id,
            "nomePrestazione": self.__nomePrestazione,
            "durataMinuti": self.__durataMinuti,
            "costoBase": self.__costoBase
        }