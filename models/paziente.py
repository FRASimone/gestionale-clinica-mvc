class Paziente:
    def __init__(self, cf: str, nome: str, cognome: str, email: str, telefono: str, is_agonista: bool):
        self.__cf = cf
        self.__nome = nome
        self.__cognome = cognome
        self.__email = email
        self.__telefono = telefono
        self.__is_agonista = is_agonista
        
        self.__cartella_clinica = None 
        self.__lista_fatture: list = []

    def getCf(self) -> str:
        return self.__cf

    def getDatiPaziente(self) -> dict:
        """Restituisce i dati impacchettati in un dizionario per la View."""
        return {
            "cf": self.__cf,
            "nome": self.__nome,
            "cognome": self.__cognome,
            "email": self.__email,
            "telefono": self.__telefono,
            "isAgonista": self.__is_agonista
        }

    def aggiornaDati(self, nuovi_dati: dict) -> bool:
        """Aggiorna lo stato interno dell'oggetto."""
        try:
            if "email" in nuovi_dati:
                self.__email = nuovi_dati["email"]
            if "telefono" in nuovi_dati:
                self.__telefono = nuovi_dati["telefono"]
            return True
        except Exception:
            return False

    def setStatoAgonista(self, stato: bool) -> None:
        self.__is_agonista = stato