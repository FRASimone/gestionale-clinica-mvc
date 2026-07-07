class Report:
    def __init__(self, id: int, annoRiferimento: int, meseRiferimento: int, tipoReport: str, datiAggregati: dict):
        self.id = id
        self.annoRiferimento = annoRiferimento
        self.meseRiferimento = meseRiferimento
        self.tipoReport = tipoReport
        self.datiAggregati = datiAggregati

    def getDatiReport(self) -> dict:
        """
        Restituisce un dizionario contenente tutte le informazioni del report, 
        inclusi i dati aggregati, pronto per essere passato alla View.
        """
        return {
            "id": self.id,
            "tipoReport": self.tipoReport,
            "annoRiferimento": self.annoRiferimento,
            "meseRiferimento": self.meseRiferimento,
            "datiAggregati": self.datiAggregati
        }