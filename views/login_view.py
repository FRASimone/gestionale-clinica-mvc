from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox, QFormLayout, QInputDialog)
from PyQt6.QtCore import Qt

# Importiamo il controller
from controllers.gestore_anagrafica import GestoreAnagrafica
from views.dashboard_segreteria import DashboardSegreteria
from views.dashboard_medico import DashboardMedico
from views.dashboard_amministratore import DashboardAmministratore

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accesso - Gestionale Clinica")
        self.resize(400, 350)
        
        # Inizializziamo il Controller. Ora la View ha accesso alla logica
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
        # crea la riga e le da un nome .input_email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Inserisci la tua email")
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Inserisci la password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.combo_ruolo = QComboBox()
        self.combo_ruolo.addItems(["Medico", "Segretario", "Amministratore"])
        # collega l'etichetta e il dato alla riga
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Password:", self.input_password)
        form_layout.addRow("Ruolo:", self.combo_ruolo)
        
        layout.addLayout(form_layout)

        # Bottone principale di Login
        self.btn_login = QPushButton("Accedi")
        # chiamata al metodo della view del login
        self.btn_login.clicked.connect(self.handle_login_click)
        layout.addWidget(self.btn_login)

        # Bottone per il Recupero Password (Requisito funz e non funz)
        self.btn_recupero = QPushButton("Hai dimenticato la password?")
        self.btn_recupero.setFlat(True) # Lo fa sembrare un link testuale invece di un bottone
        self.btn_recupero.setStyleSheet("color: red; text-decoration: underline;")
        # connessione al metodo della view per il recupero
        self.btn_recupero.clicked.connect(self.handle_recupero_click)
        layout.addWidget(self.btn_recupero)

    def handle_login_click(self):
        """Scatta al click su Accedi e smista l'utente nella dashboard corretta."""
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        ruolo = self.combo_ruolo.currentText()
        
        if not email or not password:
            QMessageBox.warning(self, "Errore", "Per favore, compila tutti i campi.")
            return

        # La View chiede al Controller di verificare le credenziali
        utente_loggato, stato = self.gestore.login(email, password, ruolo)

        if stato == "ok":
            QMessageBox.information(self, "Successo", f"Accesso effettuato!\nBenvenuto: {utente_loggato.getInfo()}")
            
            # --- APRIAMO LA DASHBOARD CORRETTA ---
            if ruolo == "Medico":
                self.dashboard = DashboardMedico(id_medico=utente_loggato.getId(), nome_medico=utente_loggato.getCognome())
            elif ruolo == "Segretario":
                self.dashboard = DashboardSegreteria(utente_loggato=utente_loggato)
            elif ruolo == "Amministratore":
                nome_completo = f"{utente_loggato.getNome()} {utente_loggato.getCognome()}"
                self.dashboard = DashboardAmministratore(
                    id_admin=utente_loggato.getId(),
                    nome_admin=nome_completo
                )
            # mostra la dashboard e chiude il login
            self.dashboard.show()
            self.close()

        elif stato == "utente_inesistente":
            QMessageBox.critical(self, "Errore di Autenticazione", "Nessun dipendente trovato con questa email.")

        elif stato == "credenziali_errate":
            QMessageBox.critical(self, "Errore di Autenticazione", "Email, password o ruolo non corretti.")

    def handle_recupero_click(self):
        """Scatta al click sul link di recupero password."""
        # Apre un piccolo pop-up nativo di PyQt per chiedere l'email
        email, confermato = QInputDialog.getText(self, "Recupero Password", "Inserisci l'email del tuo account:")
        
        if confermato and email.strip():
            # Passiamo al gestore Anagrafica l'email e chiamiamo il metodo di recupero
            successo, messaggio = self.gestore.recuperaCredenziali(email.strip())
            
            if successo:
                QMessageBox.information(self, "Email inviata", messaggio)
            else:
                QMessageBox.warning(self, "Errore", messaggio)