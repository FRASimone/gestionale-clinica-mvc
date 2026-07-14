from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QMessageBox)
from controllers.gestore_clinica import GestoreClinica, AccessoNegatoError

class CartellaClinicaDialog(QDialog):
    def __init__(self, cf_paziente: str, ruolo_utente="Medico", parent=None):
        super().__init__(parent)
        self.gestore = GestoreClinica()
        self.cf_paziente = cf_paziente
        self.ruolo_utente = ruolo_utente

        self.setWindowTitle(f"Cartella Clinica - Anamnesi Paziente {self.cf_paziente}")
        self.resize(450, 400)

        self._build_ui()
        self._carica_anamnesi()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        titolo = QLabel("Storia Clinica e Anamnesi")
        titolo.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(titolo)

        self.label_data = QLabel("")
        self.label_data.setStyleSheet("color: gray;")
        layout.addWidget(self.label_data)

        self.input_anamnesi = QTextEdit()
        self.input_anamnesi.setPlaceholderText("Nessuna anamnesi registrata.")
        layout.addWidget(self.input_anamnesi)

        # Difesa anche in UI, oltre al controllo nel Gestore (RNF10/RNF11)
        if self.ruolo_utente == "Medico":
            self.btn_salva = QPushButton("Salva Anamnesi")
            self.btn_salva.setStyleSheet("background-color: #16A085; color: white; font-weight: bold; padding: 8px;")
            self.btn_salva.clicked.connect(self.salva_anamnesi)
            layout.addWidget(self.btn_salva)
        else:
            self.input_anamnesi.setReadOnly(True)

    def _carica_anamnesi(self):
        try:
            dati = self.gestore.getCartellaClinica(self.cf_paziente, ruolo_utente=self.ruolo_utente)
        except AccessoNegatoError as e:
            self.input_anamnesi.setReadOnly(True)
            self.label_data.setText(f"Accesso negato: {e}")
            return

        if dati:
            self.input_anamnesi.setText(dati.get("anamnesiGenerica") or "")
            self.label_data.setText(f"Cartella aperta il: {dati.get('dataCreazione', 'N/D')}")
        else:
            self.label_data.setText("Nessuna cartella clinica ancora aperta per questo paziente.")

    def salva_anamnesi(self):
        nuovo_testo = self.input_anamnesi.toPlainText().strip()
        try:
            successo = self.gestore.aggiornaAnamnesi(self.cf_paziente, nuovo_testo, ruolo_utente=self.ruolo_utente)
        except AccessoNegatoError as e:
            QMessageBox.critical(self, "Accesso Negato", str(e))
            return

        if successo:
            QMessageBox.information(self, "Successo", "Anamnesi aggiornata correttamente.")
            self._carica_anamnesi()
        else:
            QMessageBox.warning(self, "Errore", "Impossibile salvare l'anamnesi.")