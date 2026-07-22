from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox)
from controllers.gestore_anagrafica import GestoreAnagrafica
from views.scheda_paziente_view import SchedaPazienteView

class RicercaPazientiView(QWidget):
    #chi istanziera' questa classe passera' il ruolo, Medico o Segretario
    #altrimenti va di default 
    def __init__(self, ruolo_utente=""):
        super().__init__()
        self.gestore = GestoreAnagrafica()
        self.ruolo_utente = ruolo_utente # Serve per capire se mostrare bottoni extra
        #per mostrare la parte del medico o segretario
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Barra di ricerca
        layout_ricerca = QHBoxLayout()
        self.input_ricerca = QLineEdit()
        self.input_ricerca.setPlaceholderText("Cerca per CF o Cognome e premi Cerca...")
        btn_cerca = QPushButton("Cerca")
        #si collega al metodo handle ricerca della view  quando si preme il bottone cerca
        btn_cerca.clicked.connect(self.handle_ricerca)
        layout_ricerca.addWidget(self.input_ricerca)
        layout_ricerca.addWidget(btn_cerca)
        layout.addLayout(layout_ricerca)
        
        # Tabella risultati, costruisce lo scheletro
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(6)
        self.tabella.setHorizontalHeaderLabels(["CF", "Nome", "Cognome", "Email", "Telefono", "Agonista"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabella)
        
        # Bottone apertura scheda
        self.btn_apri_scheda = QPushButton("Apri Cartella Paziente Selezionato")
        self.btn_apri_scheda.setStyleSheet("background-color: #9B59B6; color: white; padding: 10px;")
        #se premuto chiama il metodo apri scheda paziente
        self.btn_apri_scheda.clicked.connect(self.apri_scheda_paziente)
        layout.addWidget(self.btn_apri_scheda)

    def handle_ricerca(self):
        #prendiamo il parametro dalla view e lo passiamo al metodo del gestore
        parametro = self.input_ricerca.text().strip()
        risultati = self.gestore.ricercaPaziente(parametro)
        self.tabella.setRowCount(0)
        
        if not risultati:
            QMessageBox.information(self, "Ricerca", "Nessun paziente trovato.")
            return
        #riempie la tabella
        self.tabella.setRowCount(len(risultati)) #creo le righe in base a quanti pazienti ci sono
        for row_idx, paziente in enumerate(risultati):
            dati = paziente.getDatiPaziente() 
            #si popola la tabella
            self.tabella.setItem(row_idx, 0, QTableWidgetItem(dati["cf"]))
            self.tabella.setItem(row_idx, 1, QTableWidgetItem(dati["nome"]))
            self.tabella.setItem(row_idx, 2, QTableWidgetItem(dati["cognome"]))
            self.tabella.setItem(row_idx, 3, QTableWidgetItem(dati["email"]))
            self.tabella.setItem(row_idx, 4, QTableWidgetItem(dati["telefono"]))
            agonista_str = "Sì" if dati["isAgonista"] else "No"
            self.tabella.setItem(row_idx, 5, QTableWidgetItem(agonista_str))

    def apri_scheda_paziente(self):
        riga = self.tabella.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un paziente dalla tabella.")
            return
            
        cf_selezionato = self.tabella.item(riga, 0).text()
        self.finestra_scheda = SchedaPazienteView(cf_paziente=cf_selezionato,
                                                  ruolo_utente=self.ruolo_utente)
        self.finestra_scheda.show()