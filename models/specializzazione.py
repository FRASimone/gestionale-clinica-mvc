class Specializzazione:
    def __init__(self, id_spec: int, nome: str, descrizione: str = ""):
        self.__id = id_spec
        self.__nome = nome
        self.__descrizione = descrizione

    def getNome(self) -> str:
        """Restituisce il nome della specializzazione."""
        return self.__nome

    def getDettagli(self) -> dict:
        """Restituisce i dettagli impacchettati in un dizionario come da UML."""
        return {
            "id": self.__id,
            "nome": self.__nome,
            "descrizione": self.__descrizione
        }