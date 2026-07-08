from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox, QFormLayout, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt

from controllers.gestore_anagrafica import GestoreAnagrafica

class RegistrazioneDipendenteView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore = GestoreAnagrafica()
        
        self.setWindowTitle("Registrazione Nuovo Personale")
        self.resize(450, 500) # Leggermente più alta per far spazio alla lista
        self._build_ui()
        self._carica_specializzazioni() # Popola la lista all'avvio

    def _build_ui(self):
        layout = QVBoxLayout(self)

        titolo = QLabel("Registra Nuovo Dipendente")
        font = titolo.font()
        font.setPointSize(14)
        font.setBold(True)
        titolo.setFont(font)
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titolo)

        form_layout = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_cognome = QLineEdit()
        self.input_email = QLineEdit()
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Minimo 8 caratteri")

        self.combo_ruolo = QComboBox()
        self.combo_ruolo.addItems(["Medico", "Segretario", "Amministratore"])
        # MAGIC TRICK: Quando il ruolo cambia, chiamiamo una funzione per nascondere/mostrare le specializzazioni
        self.combo_ruolo.currentTextChanged.connect(self.toggle_specializzazioni)

        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("Cognome:", self.input_cognome)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Password:", self.input_password)
        form_layout.addRow("Ruolo:", self.combo_ruolo)

        # --- SEZIONE SPECIALIZZAZIONI (Visibile solo per i Medici) ---
        self.label_spec = QLabel("Specializzazioni:")
        self.lista_spec = QListWidget()
        self.lista_spec.setSelectionMode(QListWidget.SelectionMode.MultiSelection) # Permette scelte multiple
        
        form_layout.addRow(self.label_spec, self.lista_spec)

        layout.addLayout(form_layout)

        btn_registra = QPushButton("Registra nel Sistema")
        btn_registra.setStyleSheet("background-color: #2980B9; color: white; font-weight: bold; padding: 10px;")
        btn_registra.clicked.connect(self.handle_registrazione)
        layout.addWidget(btn_registra)

    def _carica_specializzazioni(self):
        """Prende le specializzazioni dal DB e le mette nella UI."""
        specializzazioni = self.gestore.getTutteSpecializzazioni()
        for spec in specializzazioni:
            item = QListWidgetItem(spec["nome"])
            # Salviamo l'ID del database in modo invisibile dentro l'elemento grafico
            item.setData(Qt.ItemDataRole.UserRole, spec["id"]) 
            self.lista_spec.addItem(item)

    def toggle_specializzazioni(self, ruolo):
        """Nasconde o mostra il box specializzazioni in base al ruolo."""
        is_medico = (ruolo == "Medico")
        self.label_spec.setVisible(is_medico)
        self.lista_spec.setVisible(is_medico)

    def handle_registrazione(self):
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        ruolo = self.combo_ruolo.currentText()

        if not nome or not cognome or not email or not password:
            QMessageBox.warning(self, "Errore", "Tutti i campi sono obbligatori.")
            return

        # 1. Registriamo il dipendente base
        successo, messaggio = self.gestore.registraDipendente(nome, cognome, email, password, ruolo)

        if successo:
            # 2. Se è un medico, associamo le specializzazioni
            if ruolo == "Medico":
                id_nuovo_medico = self.gestore.getDipendenteByEmail(email)
                
                # Recuperiamo tutti gli elementi cliccati nella lista
                elementi_selezionati = self.lista_spec.selectedItems()
                for item in elementi_selezionati:
                    id_spec = item.data(Qt.ItemDataRole.UserRole)
                    self.gestore.assegnaSpecializzazione(id_nuovo_medico, id_spec)

            QMessageBox.information(self, "Successo", f"{messaggio}\n\nProfilo creato correttamente.")
            
            # Svuotiamo i campi per il prossimo
            self.input_nome.clear()
            self.input_cognome.clear()
            self.input_email.clear()
            self.input_password.clear()
            self.lista_spec.clearSelection()
        else:
            QMessageBox.warning(self, "Errore di Registrazione", messaggio)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    finestra = RegistrazioneDipendenteView()
    finestra.show()
    sys.exit(app.exec())