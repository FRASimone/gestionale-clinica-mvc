from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt

from controllers.gestore_amministrativa import GestoreAmministrativa

class GestioneAmministrativaView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore_admin = GestoreAmministrativa()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- SEZIONE SUPERIORE: Ricerca Pendenze ---
        layout_ricerca = QHBoxLayout()
        layout_ricerca.addWidget(QLabel("Cerca pendenze per CF Paziente:"))
        
        self.input_cf = QLineEdit()
        self.input_cf.setPlaceholderText("Inserisci Codice Fiscale...")
        layout_ricerca.addWidget(self.input_cf)

        btn_cerca = QPushButton("Trova Appuntamenti da Saldare")
        btn_cerca.clicked.connect(self.carica_pendenze)
        layout_ricerca.addWidget(btn_cerca)
        layout.addLayout(layout_ricerca)

        # --- SEZIONE CENTRALE: Tabella Appuntamenti ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(4)
        self.tabella.setHorizontalHeaderLabels(["ID", "Data Visita", "Prestazione", "Importo (€)"])
        self.tabella.hideColumn(0) # Nascondiamo l'ID dell'appuntamento (serve solo al codice)
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabella)

        # --- SEZIONE INFERIORE: Controlli di Pagamento e Fatturazione ---
        layout_pagamento = QHBoxLayout()
        
        layout_pagamento.addWidget(QLabel("Metodo Pagamento:"))
        self.combo_metodo_pagamento = QComboBox()
        self.combo_metodo_pagamento.addItems(["Contanti", "Carta di Credito", "Bancomat", "Bonifico"])
        layout_pagamento.addWidget(self.combo_metodo_pagamento)

        layout_pagamento.addWidget(QLabel("Emissione Fattura:"))
        self.combo_metodo_fattura = QComboBox()
        self.combo_metodo_fattura.addItems(["Email (Telematico)", "Stampa Cartacea"])
        layout_pagamento.addWidget(self.combo_metodo_fattura)

        layout.addLayout(layout_pagamento)

        self.btn_paga_emetti = QPushButton("Registra Pagamento ed Emetti Fattura")
        self.btn_paga_emetti.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold; padding: 12px;")
        self.btn_paga_emetti.clicked.connect(self.processa_transazione)
        layout.addWidget(self.btn_paga_emetti)

    def carica_pendenze(self):
        cf = self.input_cf.text().strip()
        if not cf:
            QMessageBox.warning(self, "Attenzione", "Inserisci il Codice Fiscale del paziente.")
            return

        pendenze = self.gestore_admin.getAppuntamentiDaSaldare(cf)
        self.tabella.setRowCount(0)

        if not pendenze:
            QMessageBox.information(self, "Info", "Nessun appuntamento da saldare trovato per questo CF.")
            return

        self.tabella.setRowCount(len(pendenze))
        for riga, app in enumerate(pendenze):
            self.tabella.setItem(riga, 0, QTableWidgetItem(str(app['id'])))
            self.tabella.setItem(riga, 1, QTableWidgetItem(app['data']))
            self.tabella.setItem(riga, 2, QTableWidgetItem(app['nomePrestazione']))
            self.tabella.setItem(riga, 3, QTableWidgetItem(f"{app['costoBase']:.2f}"))

    def processa_transazione(self):
        riga_selezionata = self.tabella.currentRow()
        if riga_selezionata < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un appuntamento dalla tabella per procedere al pagamento.")
            return

        # Estrazione dati dalla UI
        id_appuntamento = int(self.tabella.item(riga_selezionata, 0).text())
        importo = float(self.tabella.item(riga_selezionata, 3).text())
        metodo_pagamento = self.combo_metodo_pagamento.currentText()
        metodo_fattura = "Email" if "Email" in self.combo_metodo_fattura.currentText() else "Stampa"

        # Esecuzione RF17 (Pagamento)
        id_pagamento = self.gestore_admin.registraPagamento(id_appuntamento, importo, metodo_pagamento)
        
        if id_pagamento: # Se il pagamento è andato a buon fine e abbiamo ricevuto l'ID
            # Esecuzione RF18 (Fatturazione)
            fattura_emessa = self.gestore_admin.emettiFattura(id_pagamento, metodo_fattura)
            
            if fattura_emessa:
                QMessageBox.information(self, "Successo", "Pagamento registrato e Fattura emessa correttamente!\nControlla il terminale per la simulazione.")
                self.carica_pendenze() # Ricarica la tabella (la pendenza sparirà)
            else:
                QMessageBox.warning(self, "Errore Parziale", "Pagamento registrato, ma errore durante l'emissione della fattura.")
        else:
            QMessageBox.critical(self, "Errore", "Impossibile registrare il pagamento. Potrebbe essere già stato saldato.")

# Per testarla in isolamento
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = GestioneAmministrativaView()
    finestra.show()
    sys.exit(app.exec())