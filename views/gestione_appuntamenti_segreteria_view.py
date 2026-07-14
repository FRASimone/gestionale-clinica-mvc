from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from datetime import date

from controllers.gestore_clinica import GestoreClinica
from views.modifica_appuntamento_view import ModificaAppuntamentoView

class GestioneAppuntamentiSegreteriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore_clinica = GestoreClinica()
        
        self.setWindowTitle("Pannello Segreteria - Gestione Appuntamenti")
        self.resize(700, 450)
        
        self._build_ui()
        self._popola_medici()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- Filtri di ricerca ---
        filtri_layout = QHBoxLayout()
        filtri_layout.addWidget(QLabel("Filtra per Medico:"))
        self.combo_medico = QComboBox()
        filtri_layout.addWidget(self.combo_medico)

        filtri_layout.addWidget(QLabel("Data:"))
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate())
        filtri_layout.addWidget(self.input_data)

        btn_cerca = QPushButton("Cerca Appuntamenti")
        btn_cerca.clicked.connect(self.carica_appuntamenti)
        filtri_layout.addWidget(btn_cerca)
        layout.addLayout(filtri_layout)

        # --- Tabella Risultati ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(5)
        self.tabella.setHorizontalHeaderLabels(["ID", "Orario", "Paziente", "Prestazione", "Stato"])
        self.tabella.hideColumn(0) # Nascondiamo l'ID
        
        header = self.tabella.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabella)

        # --- Bottoni Amministrativi (RF13 e RF14) ---
        bottoni_layout = QHBoxLayout()
        
        self.btn_modifica = QPushButton("Modifica Orario/Data")
        self.btn_modifica.setStyleSheet("background-color: #F39C12; color: white; font-weight: bold; padding: 10px;")
        self.btn_modifica.clicked.connect(self.apri_modifica)
        bottoni_layout.addWidget(self.btn_modifica)

        self.btn_cancella = QPushButton("Cancella Appuntamento")
        self.btn_cancella.setStyleSheet("background-color: #E74C3C; color: white; font-weight: bold; padding: 10px;")
        self.btn_cancella.clicked.connect(self.cancella_selezionato)
        bottoni_layout.addWidget(self.btn_cancella)

        layout.addLayout(bottoni_layout)

    def _popola_medici(self):
        medici = self.gestore_clinica.getTuttiMedici()
        for medico in medici:
            self.combo_medico.addItem(f"Dott. {medico['nome']} {medico['cognome']}", medico['id'])

    def carica_appuntamenti(self):
        id_medico = self.combo_medico.currentData()
        qdata = self.input_data.date()
        data_obj = date(qdata.year(), qdata.month(), qdata.day())

        # Riutilizziamo lo stesso metodo del Controller usato per l'Agenda!
        appuntamenti = self.gestore_clinica.getAgendaMedico(id_medico, data_obj)

        self.tabella.setRowCount(0)
        for riga, app in enumerate(appuntamenti):
            self.tabella.insertRow(riga)
            paziente_completo = f"{app['nome_paziente']} {app['cognome_paziente']} ({app['cf_paziente']})"
            
            self.tabella.setItem(riga, 0, QTableWidgetItem(str(app['id_appuntamento'])))
            self.tabella.setItem(riga, 1, QTableWidgetItem(str(app['oraInizio'])))
            self.tabella.setItem(riga, 2, QTableWidgetItem(paziente_completo))
            self.tabella.setItem(riga, 3, QTableWidgetItem(str(app['nomePrestazione'])))
            self.tabella.setItem(riga, 4, QTableWidgetItem(str(app['stato'])))

    def apri_modifica(self):
        riga_selezionata = self.tabella.currentRow()
        if riga_selezionata < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un appuntamento da modificare.")
            return

        stato = self.tabella.item(riga_selezionata, 4).text()
        if stato == "Completato":
            QMessageBox.warning(self, "Errore", "Impossibile modificare un appuntamento già completato dal medico.")
            return

        id_selezionato = int(self.tabella.item(riga_selezionata, 0).text())
        self.finestra_modifica = ModificaAppuntamentoView(id_appuntamento=id_selezionato)
        self.finestra_modifica.show()

    def cancella_selezionato(self):
        riga_selezionata = self.tabella.currentRow()
        if riga_selezionata < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un appuntamento da annullare.")
            return

        stato = self.tabella.item(riga_selezionata, 4).text()
        
        # Nuovi controlli di sicurezza basati sugli stati
        if stato == "Completato":
            QMessageBox.warning(self, "Errore", "Impossibile annullare un appuntamento già completato dal medico.")
            return
        if stato == "Annullato":
            QMessageBox.information(self, "Info", "Questo appuntamento è già stato annullato.")
            return

        # Finestra di conferma
        risposta = QMessageBox.question(
            self, "Conferma Annullamento", 
            "Sei sicuro di voler cambiare lo stato di questo appuntamento in 'Annullato'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if risposta == QMessageBox.StandardButton.Yes:
            id_selezionato = int(self.tabella.item(riga_selezionata, 0).text())
            
            # CHIAMIAMO IL TUO METODO ORIGINALE
            successo = self.gestore_clinica.annullaAppuntamento(id_selezionato)
            
            if successo:
                QMessageBox.information(self, "Successo", "Appuntamento annullato correttamente.")
                self.carica_appuntamenti() # Aggiorna la tabella, vedrai lo stato cambiare in 'Annullato'
            else:
                QMessageBox.warning(self, "Errore", "Impossibile annullare l'appuntamento.")

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = GestioneAppuntamentiSegreteriaView()
    finestra.show()
    sys.exit(app.exec())