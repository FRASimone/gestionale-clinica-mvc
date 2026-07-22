class Paziente:
    def __init__(self, cf: str, nome: str, cognome: str, email: str, telefono: str, is_agonista: bool):
        self.__cf = cf # chiave naturale (Codice Fiscale) — è la Primary Key nel DB
        self.__nome = nome
        self.__cognome = cognome
        self.__email = email
        self.__telefono = telefono
        self.__is_agonista = is_agonista
        
        self.__cartellaClinica = None 
        self.__listaFatture: list = []

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
        
    def getCartellaClinica(self):
        return self.__cartellaClinica
    
    def setCartellaClinica(self, cartella) -> None:
        self.__cartellaClinica = cartella

    def getListaFatture(self) -> list:
        return self.__listaFatture
    
    def aggiungiFattura(self, fattura) -> None:
        self.__listaFatture.append(fattura)
    
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