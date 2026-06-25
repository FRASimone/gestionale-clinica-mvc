class Dipendente:
    """Classe madre per tutto il personale della clinica."""
    def __init__(self, id_dipendente: int, nome: str, cognome: str, email: str, password: str, ruolo: str):
        self.__id = id_dipendente
        self.__nome = nome
        self.__cognome = cognome
        self.__email = email
        self.__password = password
        self.__ruolo = ruolo

    # --- Getters ---
    def getId(self) -> int:
        return self.__id

    def getInfo(self) -> str:
        return f"{self.__nome} {self.__cognome} ({self.__ruolo})"

    def getRuolo(self) -> str:
        return self.__ruolo
        
    def getEmail(self) -> str:
        return self.__email

    # --- Setters ---
    def setPassword(self, nuova_password: str) -> None:
        self.__password = nuova_password


class Medico(Dipendente):
    def __init__(self, id_dipendente: int, nome: str, cognome: str, email: str, password: str):
        super().__init__(id_dipendente, nome, cognome, email, password, "Medico")
        self.__appuntamenti: list = []
        self.__specializzazioni: list = []

    def getSpecializzazioni(self) -> list:
        return self.__specializzazioni
    
    def getAppuntamenti(self) -> list:
        return self.__appuntamenti
    #appena aggiunto
    def aggiungiAppuntamento(self, appuntamento) -> None:
        """Metodo utile per popolare la lista dal Controller"""
        self.__appuntamenti.append(appuntamento)


class Segretario(Dipendente):
    def __init__(self, id_dipendente: int, nome: str, cognome: str, email: str, password: str):
        super().__init__(id_dipendente, nome, cognome, email, password, "Segretario")


class Amministratore(Dipendente):
    def __init__(self, id_dipendente: int, nome: str, cognome: str, email: str, password: str):
        super().__init__(id_dipendente, nome, cognome, email, password, "Amministratore")