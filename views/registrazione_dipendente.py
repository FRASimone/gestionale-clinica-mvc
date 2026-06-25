from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox, QFormLayout)
from PyQt6.QtCore import Qt

# Importiamo il "motore"
from controllers.gestore_anagrafica import GestoreAnagrafica

class RegistrazioneDipendenteView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore = GestoreAnagrafica()
        
        self.setWindowTitle("Registrazione Nuovo Personale")
        self.resize(400, 350)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Titolo
        titolo = QLabel("Registra Nuovo Dipendente")
        font = titolo.font()
        font.setPointSize(14)
        font.setBold(True)
        titolo.setFont(font)
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titolo)

        # Form di inserimento
        form_layout = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_cognome = QLineEdit()
        self.input_email = QLineEdit()
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Minimo 8 caratteri") # Promemoria del vostro requisito

        self.combo_ruolo = QComboBox()
        self.combo_ruolo.addItems(["Medico", "Segretario", "Amministratore"])

        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("Cognome:", self.input_cognome)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Password:", self.input_password)
        form_layout.addRow("Ruolo:", self.combo_ruolo)

        layout.addLayout(form_layout)

        # Bottone di invio
        btn_registra = QPushButton("Registra nel Sistema")
        btn_registra.clicked.connect(self.handle_registrazione)
        layout.addWidget(btn_registra)

    def handle_registrazione(self):
        """Passa i dati al Controller per il salvataggio."""
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        ruolo = self.combo_ruolo.currentText()

        # Controllo base della View sui campi vuoti
        if not nome or not cognome or not email or not password:
            QMessageBox.warning(self, "Errore", "Tutti i campi sono obbligatori.")
            return

        # LA VIEW CHIEDE AL CONTROLLER DI FARE I CONTROLLI E SALVARE
        successo, messaggio = self.gestore.registraDipendente(nome, cognome, email, password, ruolo)

        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            # Svuotiamo i campi dopo un salvataggio riuscito
            self.input_nome.clear()
            self.input_cognome.clear()
            self.input_email.clear()
            self.input_password.clear()
        else:
            QMessageBox.warning(self, "Errore di Registrazione", messaggio)
# --- TRUCCO PER TESTARE SUBITO QUESTA FINESTRA ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = RegistrazioneDipendenteView()
    finestra.show()
    sys.exit(app.exec())