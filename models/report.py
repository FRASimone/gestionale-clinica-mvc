class Report:
    def __init__(self, id: int, annoRiferimento: int, meseRiferimento: int, tipoReport: str, datiAggregati: dict):
        self.__id = id
        self.__annoRiferimento = annoRiferimento
        self.__meseRiferimento = meseRiferimento
        self.__tipoReport = tipoReport
        self.__datiAggregati = datiAggregati

    def getDatiReport(self) -> dict:
        return {
            "id": self.__id,
            "tipoReport": self.__tipoReport,
            "annoRiferimento": self.__annoRiferimento,
            "meseRiferimento": self.__meseRiferimento,
            "datiAggregati": self.__datiAggregati
        }