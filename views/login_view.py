from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox, QFormLayout, QInputDialog)
from PyQt6.QtCore import Qt

# Importiamo il controller
from controllers.gestore_anagrafica import GestoreAnagrafica

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accesso - Gestionale Clinica")
        self.resize(400, 350)
        
        # Inizializziamo il Controller. Ora la View ha accesso alla logica!
        self.gestore = GestoreAnagrafica()
        # Chiamiamo il metodo per costruire l'interfaccia
        self._build_ui()

    def _build_ui(self):
        # Layout principale verticale
        layout = QVBoxLayout(self)
        # Titolo
        titolo = QLabel("Benvenuto")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = titolo.font()
        font.setPointSize(16)
        font.setBold(True)
        titolo.setFont(font)
        layout.addWidget(titolo)
        
        # Form per l'inserimento dati
        form_layout = QFormLayout()
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Inserisci la tua email")
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Inserisci la password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.combo_ruolo = QComboBox()
        self.combo_ruolo.addItems(["Medico", "Segretario", "Amministratore"])
        
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Password:", self.input_password)
        form_layout.addRow("Ruolo:", self.combo_ruolo)
        
        layout.addLayout(form_layout)

        # Bottone principale di Login
        self.btn_login = QPushButton("Accedi")
        self.btn_login.clicked.connect(self.handle_login_click)
        layout.addWidget(self.btn_login)

        # Bottone per il Recupero Password (Requisito non funzionale)
        self.btn_recupero = QPushButton("Hai dimenticato la password?")
        self.btn_recupero.setFlat(True) # Lo fa sembrare un link testuale invece di un bottone
        self.btn_recupero.setStyleSheet("color: red; text-decoration: underline;")
        self.btn_recupero.clicked.connect(self.handle_recupero_click)
        layout.addWidget(self.btn_recupero)

    def handle_login_click(self):
        """Scatta al click su Accedi e passa i dati al Controller."""
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        ruolo = self.combo_ruolo.currentText()
        # Controllo base prima di passarlo al Controller
        if not email or not password:
            QMessageBox.warning(self, "Errore", "Per favore, compila tutti i campi.")
            return


        # La View chiede al Controller di fare il lavoro
        utente_loggato = self.gestore.login(email, password, ruolo)

        if utente_loggato:
            # Il login ha funzionato, il Controller ha restituito l'oggetto (es. un Medico).
            # Usiamo il metodo polimorfico getInfo() del Model per salutarlo.
            QMessageBox.information(self, "Successo", f"Accesso effettuato!\nBenvenuto: {utente_loggato.getInfo()}")
            
            # Qui in futuro chiuderemo questa finestra e apriremo la dashboard corrispondente
        else:
            QMessageBox.critical(self, "Errore di Autenticazione", "Email, password o ruolo non corretti.")

    def handle_recupero_click(self):
        """Scatta al click sul link di recupero password."""
        # Apre un piccolo pop-up nativo di PyQt per chiedere l'email
        email, confermato = QInputDialog.getText(self, "Recupero Password", "Inserisci l'email del tuo account:")
        
        if confermato and email.strip():
            # Passiamo la palla al Controller
            successo, messaggio = self.gestore.recuperaCredenziali(email.strip())
            
            if successo:
                QMessageBox.information(self, "Email inviata", messaggio)
            else:
                QMessageBox.warning(self, "Errore", messaggio)