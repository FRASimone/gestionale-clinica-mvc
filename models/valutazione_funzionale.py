class ValutazioneFunzionale:
    """
    Rappresenta il referto medico compilato dal Medico dopo una visita: 
    anomalie riscontrate, note, prevenzione overtraining, e un voto
    clinico da 1 a 10."""
    def __init__(self, id_valutazione: int, anomalie: str, noteAggiuntive: str, prevOvertraining: str, valutazioneClinica: int):
        self.__id = id_valutazione
        self.__anomalie = anomalie
        self.__noteAggiuntive = noteAggiuntive
        self.__prevOvertraining = prevOvertraining
        self.__valutazioneClinica = valutazioneClinica

    def aggiornaNote(self, nuove_note: str) -> None:
        self.__noteAggiuntive = nuove_note

    def getDettagli(self) -> dict:
        return {
            "id": self.__id,
            "anomalie": self.__anomalie,
            "noteAggiuntive": self.__noteAggiuntive,
            "prevOvertraining": self.__prevOvertraining,
            "valutazioneClinica": self.__valutazioneClinica
        }