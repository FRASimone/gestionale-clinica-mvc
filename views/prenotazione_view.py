from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                             QDateEdit, QTimeEdit, QPushButton, QMessageBox, QLabel, QDialog)
from PyQt6.QtCore import QDate, QTime, Qt
from datetime import date, time 

from views.registrazione_paziente_dialog import RegistrazionePazienteDialog
from controllers.gestore_clinica import GestoreClinica

class PrenotazioneView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore_clinica = GestoreClinica()
        
        self.setWindowTitle("Prenotazione Nuovo Appuntamento")
        self.resize(450, 300)
        
        self._build_ui()
        #chiamata iniziale per popolare la schermata
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
        self.input_data.setMinimumDate(QDate.currentDate()) # Blocca le date passate
        self.input_ora = QTimeEdit()
        self.input_ora.setTime(QTime(9, 0)) # Orario di default 09:00

        # Menù a tendina
        self.combo_paziente = QComboBox()
        self.combo_medico = QComboBox()
        self.combo_prestazione = QComboBox()

        form_layout.addRow("Paziente:", self.combo_paziente)
        
        btn_nuovo_paziente = QPushButton("+ Registra Nuovo Paziente")
        btn_nuovo_paziente.setStyleSheet("background-color: #3498DB; color: white;")
        btn_nuovo_paziente.clicked.connect(self.apri_registrazione_rapida)
        form_layout.addRow("", btn_nuovo_paziente)
        
        form_layout.addRow("Medico:", self.combo_medico)
        form_layout.addRow("Prestazione:", self.combo_prestazione)
        form_layout.addRow("Data Visita:", self.input_data)
        form_layout.addRow("Ora Inizio:", self.input_ora)

        layout.addLayout(form_layout)

        # Bottone
        btn_prenota = QPushButton("Conferma Prenotazione")
        #quando premuto si avvia il metodo della view handle prenotazione
        btn_prenota.clicked.connect(self.handle_prenotazione)
        layout.addWidget(btn_prenota)

    def _popola_tendine(self):
        """Richiede i dati al Controller e riempie le tendine."""
        # 1. recupera tutti i pazienti
        for paz in self.gestore_clinica.getTuttiPazienti():
            testo_visibile = f"{paz['nome']} {paz['cognome']} ({paz['cf']})"
            # addItem(testo_mostrato, dato_nascosto)
            self.combo_paziente.addItem(testo_visibile, paz['cf'])

        # 2. recupera tutti i medici
        for medico in self.gestore_clinica.getTuttiMedici():
            testo_visibile = f"Dott. {medico['nome']} {medico['cognome']}"
            self.combo_medico.addItem(testo_visibile, medico['id'])

        # 3. recupera tutte le prestazioni
        for prest in self.gestore_clinica.getPrestazioniDisponibili():
            # prest è un oggetto Model, usiamo il getter!
            info = prest.getInfoPrestazione()
            testo_visibile = f"{info['nomePrestazione']} ({info['durataMinuti']} min - {info['costoBase']}€)"
            self.combo_prestazione.addItem(testo_visibile, info['id'])
            #mostra all utente il testo ma nasconde l'id che serve al DB

    def handle_prenotazione(self):
        """Raccoglie i dati, li formatta e chiama il Controller."""
        
        # Estraiamo i dati nascosti (currentData) associati alla combo passati dal popola_tendine
        cf_paziente = self.combo_paziente.currentData()
        id_medico = self.combo_medico.currentData()
        id_prestazione = self.combo_prestazione.currentData()
        
        # Blocchiamo se il database è vuoto e le tendine non hanno dati
        if not cf_paziente or not id_medico or not id_prestazione:
            QMessageBox.warning(self, "Errore", "Assicurati di aver selezionato Paziente, Medico e Prestazione.")
            return

        # Estraiamo Data e Ora e li convertiamo negli oggetti Python (date e time)
        qdata = self.input_data.date()
        qora = self.input_ora.time()
        
        data_obj = date(qdata.year(), qdata.month(), qdata.day())
        ora_obj = time(qora.hour(), qora.minute())

        # CHIAMATA AL CONTROLLER gestore Clinica
        successo, messaggio  = self.gestore_clinica.creaAppuntamento(data_obj, ora_obj, cf_paziente, id_medico, id_prestazione)

        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            self.close() # Chiude la finestra
        else:
            QMessageBox.warning(self, "Impossibile Prenotare", messaggio)

    def apri_registrazione_rapida(self):
        dialog = RegistrazionePazienteDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Il paziente è stato salvato! 
            # 1. Ricarichiamo TUTTI i pazienti dal DB
            self.combo_paziente.clear()
            # Questo è il for che avevi nel metodo _popola_tendine()
            for paz in self.gestore_clinica.getTuttiPazienti():
                testo = f"{paz['nome']} {paz['cognome']} ({paz['cf']})"
                self.combo_paziente.addItem(testo, paz['cf'])
            
            # 2. Selezioniamo automaticamente quello appena creato
            nuovo_cf = dialog.cf_creato
            indice = self.combo_paziente.findData(nuovo_cf)
            if indice != -1:
                self.combo_paziente.setCurrentIndex(indice)
                
                
# --- TEST DIRETTO DELLA VIEW ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = PrenotazioneView()
    finestra.show()
    sys.exit(app.exec())