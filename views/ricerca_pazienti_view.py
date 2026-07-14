from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox)
from controllers.gestore_anagrafica import GestoreAnagrafica
from views.scheda_paziente_view import SchedaPazienteView

class RicercaPazientiView(QWidget):
    def __init__(self, ruolo_utente=""):
        super().__init__()
        self.gestore = GestoreAnagrafica()
        self.ruolo_utente = ruolo_utente # Serve per capire se mostrare bottoni extra
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Barra di ricerca
        layout_ricerca = QHBoxLayout()
        self.input_ricerca = QLineEdit()
        self.input_ricerca.setPlaceholderText("Cerca per CF o Cognome e premi Cerca...")
        btn_cerca = QPushButton("Cerca")
        btn_cerca.clicked.connect(self.handle_ricerca)
        layout_ricerca.addWidget(self.input_ricerca)
        layout_ricerca.addWidget(btn_cerca)
        layout.addLayout(layout_ricerca)
        
        # Tabella risultati
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(6)
        self.tabella.setHorizontalHeaderLabels(["CF", "Nome", "Cognome", "Email", "Telefono", "Agonista"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabella)
        
        # Bottone apertura scheda
        self.btn_apri_scheda = QPushButton("Apri Cartella Paziente Selezionato")
        self.btn_apri_scheda.setStyleSheet("background-color: #9B59B6; color: white; padding: 10px;")
        self.btn_apri_scheda.clicked.connect(self.apri_scheda_paziente)
        layout.addWidget(self.btn_apri_scheda)

    def handle_ricerca(self):
        # [COPIA QUI DENTRO L'INTERO METODO handle_ricerca CHE HAI NELLA SEGRETERIA]
        parametro = self.input_ricerca.text().strip()
        risultati = self.gestore.ricercaPaziente(parametro)
        self.tabella.setRowCount(0)
        
        if not risultati:
            QMessageBox.information(self, "Ricerca", "Nessun paziente trovato.")
            return
            
        self.tabella.setRowCount(len(risultati))
        for row_idx, paziente in enumerate(risultati):
            dati = paziente.getDatiPaziente() 
            self.tabella.setItem(row_idx, 0, QTableWidgetItem(dati["cf"]))
            self.tabella.setItem(row_idx, 1, QTableWidgetItem(dati["nome"]))
            self.tabella.setItem(row_idx, 2, QTableWidgetItem(dati["cognome"]))
            self.tabella.setItem(row_idx, 3, QTableWidgetItem(dati["email"]))
            self.tabella.setItem(row_idx, 4, QTableWidgetItem(dati["telefono"]))
            agonista_str = "Sì" if dati["isAgonista"] else "No"
            self.tabella.setItem(row_idx, 5, QTableWidgetItem(agonista_str))

    def apri_scheda_paziente(self):
        # [COPIA QUI DENTRO L'INTERO METODO apri_scheda_segreteria]
        riga = self.tabella.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un paziente dalla tabella.")
            return
            
        cf_selezionato = self.tabella.item(riga, 0).text()
        self.finestra_scheda = SchedaPazienteView(cf_paziente=cf_selezionato,
                                                  ruolo_utente=self.ruolo_utente)
        self.finestra_scheda.show()