from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QDateEdit, 
                             QTimeEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import QDate, QTime, Qt
from datetime import date, time

from controllers.gestore_clinica import GestoreClinica

class ModificaAppuntamentoView(QWidget):
    def __init__(self, id_appuntamento: int):
        super().__init__()
        self.gestore_clinica = GestoreClinica()
        self.id_appuntamento = id_appuntamento
        
        self.setWindowTitle(f"Modifica Appuntamento #{self.id_appuntamento}")
        self.resize(350, 250)
        
        self._build_ui()
        #viene chiamato subito il metodo per popolare i dati che verranno cambiati
        self._carica_dati_attuali()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.label_paziente = QLabel("Caricamento paziente...")
        self.label_paziente.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.label_paziente.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_paziente)

        form = QFormLayout()
        
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setMinimumDate(QDate.currentDate()) # Blocca le date passate
        form.addRow("Nuova Data:", self.input_data)

        self.input_ora = QTimeEdit()
        self.input_ora.setDisplayFormat("HH:mm")
        form.addRow("Nuovo Orario:", self.input_ora)

        layout.addLayout(form)

        btn_salva = QPushButton("Salva Modifiche")
        btn_salva.setStyleSheet("background-color: #F39C12; color: white; font-weight: bold; padding: 8px;")
        #bottone Salva che se premuto chiama il metodo della view salva modifiche
        btn_salva.clicked.connect(self.salva_modifiche)
        layout.addWidget(btn_salva)

    def _carica_dati_attuali(self):
        dati = self.gestore_clinica.getDettagliAppuntamento(self.id_appuntamento)
        if dati:
            self.label_paziente.setText(f"Paziente: {dati['nome']} {dati['cognome']}")
            
            # Impostiamo la data attuale nel widget
            #dal database arrivano in forma di stringa, si trasforano in interi
            #e poi si crea l oggetto QDate
            anno, mese, giorno = map(int, dati['data'].split('-'))
            self.input_data.setDate(QDate(anno, mese, giorno))
            
            # Impostiamo l'ora attuale nel widget
            #la logica e' uguale per la data
            ore, minuti = map(int, dati['oraInizio'].split(':')[:2])
            self.input_ora.setTime(QTime(ore, minuti))

    def salva_modifiche(self):
        # 1. Estraiamo la Data (oggetto date)
        qdata = self.input_data.date()
        nuova_data_obj = date(qdata.year(), qdata.month(), qdata.day())
        
        # 2. Estraiamo l'Ora
        qora = self.input_ora.time()
        nuova_ora_obj = time(qora.hour(), qora.minute())

        # 3. Chiamiamo il metodo del gestore Clinica modifica orario Appuntamento 
        #passando la nuova data e la nuova ora
        successo, messaggio = self.gestore_clinica.modificaOrarioAppuntamento(
            self.id_appuntamento, nuova_data_obj, nuova_ora_obj
        )
        
        # 4. Mostriamo il messaggio appropriato in base all'esito
        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            self.close()
        else:
            # Se c'è un conflitto, mostriamo il messaggio di errore calcolato dal Controller
            QMessageBox.warning(self, "Impossibile Modificare", messaggio)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Testa con l'ID 1 (assicurati esista!)
    finestra = ModificaAppuntamentoView(id_appuntamento=1)
    finestra.show()
    sys.exit(app.exec())