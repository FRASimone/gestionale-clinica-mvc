from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QMessageBox, QGroupBox)


from controllers.gestore_anagrafica import GestoreAnagrafica

class GestioneRuoliView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore = GestoreAnagrafica() # Istanzia il controller
        self._build_ui()
        self.carica_dipendenti()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- TABELLA DIPENDENTI ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(5)
        self.tabella.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Email", "Ruolo Attuale"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabella)

        # --- PANNELLO MODIFICA RUOLO ---
        group_modifica = QGroupBox("Modifica Permessi e Ruolo")
        layout_modifica = QHBoxLayout()

        layout_modifica.addWidget(QLabel("Nuovo Ruolo:"))
        
        self.combo_nuovo_ruolo = QComboBox()
        self.combo_nuovo_ruolo.addItems(["Medico", "Segretario", "Amministratore"])
        layout_modifica.addWidget(self.combo_nuovo_ruolo)

        btn_salva = QPushButton("Aggiorna Ruolo")
        btn_salva.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold;")
        btn_salva.clicked.connect(self.aggiorna_ruolo)
        layout_modifica.addWidget(btn_salva)

        group_modifica.setLayout(layout_modifica)
        layout.addWidget(group_modifica)

    def carica_dipendenti(self):
        """Richiede al controller la lista dei dipendenti e popola la tabella."""
        risultati = self.gestore.get_tutti_dipendenti() 
        
        self.tabella.setRowCount(0)
        for riga, dipendente in enumerate(risultati):
            self.tabella.insertRow(riga)
            self.tabella.setItem(riga, 0, QTableWidgetItem(str(dipendente["id"])))
            self.tabella.setItem(riga, 1, QTableWidgetItem(dipendente["nome"]))
            self.tabella.setItem(riga, 2, QTableWidgetItem(dipendente["cognome"]))
            self.tabella.setItem(riga, 3, QTableWidgetItem(dipendente["email"]))
            self.tabella.setItem(riga, 4, QTableWidgetItem(dipendente["ruolo"]))

    def aggiorna_ruolo(self):
        riga = self.tabella.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un dipendente dalla tabella.")
            return

        id_dipendente = int(self.tabella.item(riga, 0).text())
        nuovo_ruolo = self.combo_nuovo_ruolo.currentText()
        ruolo_attuale = self.tabella.item(riga, 4).text()

        if nuovo_ruolo == ruolo_attuale:
            QMessageBox.information(self, "Info", "Il dipendente ha già questo ruolo.")
            return

        # CHIAMATA AL CONTROLLER
        successo = self.gestore.modifica_ruolo(id_dipendente, nuovo_ruolo)

        
        if successo:
            QMessageBox.information(self, "Successo", f"Ruolo aggiornato in '{nuovo_ruolo}'.")
            self.carica_dipendenti() # Ricarica per mostrare l'aggiornamento
        else:
            QMessageBox.critical(self, "Errore", "Impossibile aggiornare il ruolo.")