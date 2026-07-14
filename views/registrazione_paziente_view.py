from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QCheckBox, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from controllers.gestore_anagrafica import GestoreAnagrafica

class RegistrazionePazienteView(QWidget):
    # Segnale emesso quando il paziente viene registrato con successo.
    # Utile per aggiornare le tendine di altre viste.
    paziente_salvato = pyqtSignal(str) 

    def __init__(self):
        super().__init__()
        self.gestore = GestoreAnagrafica()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.input_cf = QLineEdit()
        self.input_nome = QLineEdit()
        self.input_cognome = QLineEdit()
        self.input_email = QLineEdit()
        self.input_telefono = QLineEdit()
        self.check_agonista = QCheckBox("Paziente Agonista")
        
        form_layout.addRow("Codice Fiscale:", self.input_cf)
        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("Cognome:", self.input_cognome)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Telefono:", self.input_telefono)
        form_layout.addRow("", self.check_agonista)
        
        layout.addLayout(form_layout)
        
        btn_aggiungi = QPushButton("Salva Paziente")
        btn_aggiungi.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold;")
        btn_aggiungi.clicked.connect(self.handle_aggiungi_paziente)
        layout.addWidget(btn_aggiungi)
        
        layout.addStretch()

    def handle_aggiungi_paziente(self):
        cf = self.input_cf.text().strip()
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        telefono = self.input_telefono.text().strip()
        is_agonista = self.check_agonista.isChecked()
        
        if not cf or not nome or not cognome:
            QMessageBox.warning(self, "Errore", "CF, Nome e Cognome obbligatori.")
            return
            
        nuovo_paziente = self.gestore.aggiungiPaziente(cf, nome, cognome, email, telefono, is_agonista)
        
        if nuovo_paziente:
            QMessageBox.information(self, "Successo", "Paziente registrato!")
            # Emette il segnale col codice fiscale appena salvato
            self.paziente_salvato.emit(cf) 
            self._pulisci_form()
        else:
            QMessageBox.critical(self, "Errore", "CF già presente o errore DB.")

    def _pulisci_form(self):
         self.input_cf.clear()
         self.input_nome.clear()
         self.input_cognome.clear()
         self.input_email.clear()
         self.input_telefono.clear()
         self.check_agonista.setChecked(False)