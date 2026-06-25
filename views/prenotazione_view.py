from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                             QDateEdit, QTimeEdit, QPushButton, QMessageBox, QLabel)
from PyQt6.QtCore import QDate, QTime, Qt
from datetime import date, time # Importiamo gli oggetti che vuole il tuo UML

from controllers.gestore_clinica import GestoreClinica

class PrenotazioneView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore_clinica = GestoreClinica()
        
        self.setWindowTitle("Prenotazione Nuovo Appuntamento")
        self.resize(450, 300)
        
        self._build_ui()
        self._popola_tendine()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        titolo = QLabel("Registra Appuntamento")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titolo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titolo)

        form_layout = QFormLayout()

        # Input Data e Ora
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True) # Mostra il calendarietto a tendina
        self.input_data.setDate(QDate.currentDate()) # Imposta data di oggi di default
        
        self.input_ora = QTimeEdit()
        self.input_ora.setTime(QTime(9, 0)) # Orario di default 09:00

        # Menù a tendina
        self.combo_paziente = QComboBox()
        self.combo_medico = QComboBox()
        self.combo_prestazione = QComboBox()

        form_layout.addRow("Paziente:", self.combo_paziente)
        form_layout.addRow("Medico:", self.combo_medico)
        form_layout.addRow("Prestazione:", self.combo_prestazione)
        form_layout.addRow("Data Visita:", self.input_data)
        form_layout.addRow("Ora Inizio:", self.input_ora)

        layout.addLayout(form_layout)

        # Bottone
        btn_prenota = QPushButton("Conferma Prenotazione")
        btn_prenota.clicked.connect(self.handle_prenotazione)
        layout.addWidget(btn_prenota)

    def _popola_tendine(self):
        """Richiede i dati al Controller e riempie le tendine."""
        # 1. Pazienti
        for paz in self.gestore_clinica.getTuttiPazienti():
            testo_visibile = f"{paz['nome']} {paz['cognome']} ({paz['cf']})"
            # addItem(testo_mostrato, dato_nascosto)
            self.combo_paziente.addItem(testo_visibile, paz['cf'])

        # 2. Medici
        for medico in self.gestore_clinica.getTuttiMedici():
            testo_visibile = f"Dott. {medico['nome']} {medico['cognome']}"
            self.combo_medico.addItem(testo_visibile, medico['id'])

        # 3. Prestazioni
        for prest in self.gestore_clinica.getPrestazioniDisponibili():
            # prest è un oggetto Model, usiamo il getter!
            info = prest.getInfoPrestazione()
            testo_visibile = f"{info['nomePrestazione']} ({info['durataMinuti']} min - {info['costoBase']}€)"
            self.combo_prestazione.addItem(testo_visibile, info['id'])

    def handle_prenotazione(self):
        """Raccoglie i dati, li formatta come da UML e chiama il Controller."""
        
        # Estraiamo i dati nascosti (userData) che corrispondono ai parametri dell'UML
        cf_paziente = self.combo_paziente.currentData()
        id_medico = self.combo_medico.currentData()
        id_prestazione = self.combo_prestazione.currentData()
        
        # Blocchiamo se il database è vuoto e le tendine non hanno dati
        if not cf_paziente or not id_medico or not id_prestazione:
            QMessageBox.warning(self, "Errore", "Assicurati di aver selezionato Paziente, Medico e Prestazione.")
            return

        # Estraiamo Data e Ora e li convertiamo negli oggetti Python (date e time) per rispettare l'UML
        qdata = self.input_data.date()
        qora = self.input_ora.time()
        
        data_obj = date(qdata.year(), qdata.month(), qdata.day())
        ora_obj = time(qora.hour(), qora.minute())

        # CHIAMATA AL CONTROLLER
        successo = self.gestore_clinica.creaAppuntamento(data_obj, ora_obj, cf_paziente, id_medico, id_prestazione)

        if successo:
            QMessageBox.information(self, "Successo", "Appuntamento prenotato e inserito in agenda!")
            self.close() # Chiude la finestra
        else:
            QMessageBox.warning(self, "Errore", "Si è verificato un problema durante la prenotazione.")

# --- TEST DIRETTO DELLA VIEW ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = PrenotazioneView()
    finestra.show()
    sys.exit(app.exec())