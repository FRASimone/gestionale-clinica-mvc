from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from datetime import date

from controllers.gestore_clinica import GestoreClinica
from views.valutazione_funzionale_view import ValutazioneFunzionaleView
from views.scheda_paziente_view import SchedaPazienteView

class AgendaMedicoView(QWidget):
    def __init__(self, ruolo_utente="Medico"):
        super().__init__()
        self.ruolo_utente = ruolo_utente
        self.gestore_clinica = GestoreClinica()
        
        self.setWindowTitle("Agenda Appuntamenti Medico")
        self.resize(600, 400)
        
        self._build_ui()
        # popola la tendina, serve poi nella dashboard per selezionare il medico
        # che sta usando la dashboard e bloccare la selezione combo box
        self._popola_medici()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- SEZIONE SUPERIORE: Filtri di ricerca ---
        filtri_layout = QHBoxLayout()
        
        filtri_layout.addWidget(QLabel("Seleziona Medico:"))
        self.combo_medico = QComboBox()
        filtri_layout.addWidget(self.combo_medico)

        filtri_layout.addWidget(QLabel("Data:"))
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate()) # Di default mostra oggi
        filtri_layout.addWidget(self.input_data)

        btn_cerca = QPushButton("Carica Agenda")
        # lambda esplicita: click manuale -> mostra sempre l'avviso se vuoto
        btn_cerca.clicked.connect(lambda: self.carica_appuntamenti(mostra_avviso=True))
        filtri_layout.addWidget(btn_cerca)

        layout.addLayout(filtri_layout)

        # --- SEZIONE INFERIORE: Tabella Risultati ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(6)
        self.tabella.setHorizontalHeaderLabels(["ID", "Orario", "Paziente", "Prestazione", "Stato", "CF"])
        
        self.tabella.hideColumn(0) # <-- NASCONDIAMO LA COLONNA ID ALL'UTENTE
        self.tabella.hideColumn(5) # Nascondi CF
        # Facciamo in modo che le colonne si allarghino per riempire lo spazio
        header = self.tabella.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # La tabella deve essere in sola lettura (non si modifica scrivendo nelle celle)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.tabella)
        
        # --- BOTTONE SOTTO LA TABELLA APPUNTAMENTI---
        self.btn_avvia_visita = QPushButton("Avvia Visita (Compila Referto)")
        self.btn_avvia_visita.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; padding: 10px;")
        #se il bottone viene premuto si avvia il metodo apri valutazione della vi
        self.btn_avvia_visita.clicked.connect(self.apri_valutazione)
        layout.addWidget(self.btn_avvia_visita)
        
        self.btn_cartella_clinica = QPushButton("Visualizza Cartella Clinica")
        self.btn_cartella_clinica.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold; padding: 10px;")
        self.btn_cartella_clinica.clicked.connect(self.apri_scheda_medico)
        layout.addWidget(self.btn_cartella_clinica)

    def _popola_medici(self):
        """Metodo di supporto per riempire la tendina dei medici."""
        medici = self.gestore_clinica.getTuttiMedici()
        for medico in medici:
            testo = f"Dott. {medico['nome']} {medico['cognome']}"
            self.combo_medico.addItem(testo, medico['id'])

    def carica_appuntamenti(self, mostra_avviso=True):
        """Chiama il Controller e riempie la tabella con i risultati.
        mostra_avviso=False viene usato per il precaricamento automatico
        all'apertura della dashboard, per non mostrare popup inutili al login."""
        id_medico = self.combo_medico.currentData()
        if not id_medico:
            if mostra_avviso:
                QMessageBox.warning(self, "Attenzione", "Nessun medico selezionato.")
            return

        # Estraiamo la data e la convertiamo nell'oggetto Python "date" come richiesto dall'UML
        qdata = self.input_data.date()
        data_obj = date(qdata.year(), qdata.month(), qdata.day())

        # CHIAMATA AL CONTROLLER Clinica con il metodo getAgendaMedico
        appuntamenti = self.gestore_clinica.getAgendaMedico(id_medico, data_obj)

        # Puliamo la tabella prima di inserire i nuovi dati
        self.tabella.setRowCount(0)

        if not appuntamenti:
            # Se la lista è vuota, avvisiamo solo se richiesto esplicitamente
            if mostra_avviso:
                QMessageBox.information(self, "Agenda", "Nessun appuntamento trovato per questa data.")
            return

       # Riempiamo la tabella riga per riga
        for riga, app in enumerate(appuntamenti):
            self.tabella.insertRow(riga)
            
            # Creiamo una stringa unica unendo Nome, Cognome e CF
            paziente_completo = f"{app['nome_paziente']} {app['cognome_paziente']} ({app['cf_paziente']})"
            
            # Creiamo gli elementi della tabella (QTableWidgetItem accetta solo testo)
            item_id = QTableWidgetItem(str(app['id_appuntamento'])) # Creiamo l'item per l'ID
            item_orario = QTableWidgetItem(str(app['oraInizio']))
            item_paziente = QTableWidgetItem(paziente_completo)
            item_prestazione = QTableWidgetItem(str(app['nomePrestazione'])) # <-- Qui abbiamo risolto il KeyError
            item_stato = QTableWidgetItem(str(app['stato']))
            item_cf = QTableWidgetItem(str(app['cf_paziente']))

            # Inseriamo gli elementi nelle rispettive colonne
            self.tabella.setItem(riga, 0, item_id)
            self.tabella.setItem(riga, 1, item_orario)
            self.tabella.setItem(riga, 2, item_paziente)
            self.tabella.setItem(riga, 3, item_prestazione)
            self.tabella.setItem(riga, 4, item_stato)
            self.tabella.setItem(riga, 5, item_cf)
        
    def apri_valutazione(self):
        """Legge la riga selezionata e apre la finestra di refertazione."""
        riga_selezionata = self.tabella.currentRow()
        
        # Controllo 1: L'utente ha selezionato qualcosa?
        if riga_selezionata < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un paziente dall'agenda per avviare la visita.")
            return
            
        # Controllo 2: La visita è già stata fatta o è stata annullata? (colonna 4 "Stato")
        stato = self.tabella.item(riga_selezionata, 4).text()
        if stato == "Completato":
            QMessageBox.information(self, "Info", "Questa visita è già stata refertata e completata.")
            return
        if stato == "Annullato":
            QMessageBox.warning(self, "Attenzione", "Impossibile avviare la visita: l'appuntamento è stato annullato.")
            return

        # Estraiamo l'ID nascosto dalla colonna 0
        id_selezionato = int(self.tabella.item(riga_selezionata, 0).text())
        #prendiamo il dato nascosto dall elemento selezionato, ovvero l'id dal combo
        id_medico_corrente = self.combo_medico.currentData()
        # Apriamo la finestra passandole l'ID!
        self.finestra_visita = ValutazioneFunzionaleView(id_appuntamento=id_selezionato, id_medico=id_medico_corrente)
        self.finestra_visita.show()
        
    def apri_scheda_medico(self):
        riga = self.tabella.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un paziente per vedere la sua cartella.")
            return
            
        cf_selezionato = self.tabella.item(riga, 5).text() # Estraiamo il CF nascosto!
        self.finestra_scheda = SchedaPazienteView(cf_paziente=cf_selezionato,
                                                  ruolo_utente=self.ruolo_utente)
        self.finestra_scheda.show()


# --- TEST DIRETTO DELLA VIEW ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = AgendaMedicoView()
    finestra.show()
    sys.exit(app.exec())