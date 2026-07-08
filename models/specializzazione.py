class Specializzazione:
    def __init__(self, id_spec: int, nome: str, dettagli: str = ""):
        self.id_spec = id_spec
        self.nome = nome
        self.dettagli = dettagli

    def getNome(self) -> str:
        """Restituisce il nome della specializzazione."""
        return self.nome

    def getDettagli(self) -> dict:
        """Restituisce i dettagli impacchettati in un dizionario come da UML."""
        return {
            "id": self.id_spec,
            "nome": self.nome,
            "descrizione": self.dettagli
        }