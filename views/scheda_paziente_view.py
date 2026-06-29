from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QCheckBox, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt

from controllers.gestore_anagrafica import GestoreAnagrafica
from controllers.gestore_clinica import GestoreClinica
from controllers.gestore_anagrafica import GestoreAnagrafica 

class SchedaPazienteView(QWidget):
    def __init__(self, cf_paziente: str):
        super().__init__()
        self.cf_paziente = cf_paziente
        self.gestore_anagrafica = GestoreAnagrafica()
        self.gestore_clinica = GestoreClinica()
        
        self.setWindowTitle(f"Cartella Clinica - Paziente: {self.cf_paziente}")
        self.resize(750, 600)
        
        self._build_ui()
        self._carica_dati_paziente()
        self._carica_storico_clinico()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- SEZIONE SUPERIORE: Dati Anagrafici (RF7) ---
        titolo_dati = QLabel("Dati Anagrafici e Contatti")
        titolo_dati.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(titolo_dati)

        form_layout = QFormLayout()
        
        # CF, Nome e Cognome sono in sola lettura (non si cambiano)
        self.input_cf = QLineEdit(self.cf_paziente)
        self.input_cf.setReadOnly(True)
        self.input_nome = QLineEdit()
        self.input_nome.setReadOnly(True)
        self.input_cognome = QLineEdit()
        self.input_cognome.setReadOnly(True)
        
        # Email, Telefono e Agonista sono modificabili
        self.input_email = QLineEdit()
        self.input_telefono = QLineEdit()
        self.check_agonista = QCheckBox("Paziente Agonista")

        form_layout.addRow("Codice Fiscale:", self.input_cf)
        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("Cognome:", self.input_cognome)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Telefono:", self.input_telefono)
        form_layout.addRow("", self.check_agonista)

        layout.addLayout(form_layout)

        btn_salva = QPushButton("Salva Modifiche Anagrafica (RF7)")
        btn_salva.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold; padding: 8px;")
        btn_salva.clicked.connect(self.salva_modifiche)
        layout.addWidget(btn_salva)

        # --- SEZIONE INFERIORE: Storico Clinico (RF8) ---
        titolo_storico = QLabel("Storico Trattamenti e Valutazioni (RF8)")
        titolo_storico.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px;")
        layout.addWidget(titolo_storico)

        self.tabella_storico = QTableWidget()
        self.tabella_storico.setColumnCount(4)
        self.tabella_storico.setHorizontalHeaderLabels(["Data", "Prestazione", "Medico", "Referto/Stato"])
        self.tabella_storico.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_storico.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabella_storico)

    def _carica_dati_paziente(self):
        """Richiede al controller i dati attuali per pre-compilare il form."""
        # Usiamo il metodo di ricerca
        risultati = self.gestore_anagrafica.ricercaPaziente(self.cf_paziente)
        
        if risultati:
            paziente = risultati[0] # Prendiamo il primo (e unico) risultato
            dati = paziente.getDatiPaziente()
            
            self.input_nome.setText(dati['nome'])
            self.input_cognome.setText(dati['cognome'])
            self.input_email.setText(dati['email'])
            self.input_telefono.setText(dati['telefono'])
            self.check_agonista.setChecked(dati['isAgonista'])

    def _carica_storico_clinico(self):
        """Richiede al controller tutte le visite passate del paziente."""
        storico = self.gestore_clinica.getStoricoPaziente(self.cf_paziente)
        
        self.tabella_storico.setRowCount(0)
        
        for riga, visita in enumerate(storico):
            self.tabella_storico.insertRow(riga)
            
            medico_completo = f"Dott. {visita['nome_medico']} {visita['cognome_medico']}"
            
            self.tabella_storico.setItem(riga, 0, QTableWidgetItem(str(visita['data'])))
            self.tabella_storico.setItem(riga, 1, QTableWidgetItem(str(visita['nomePrestazione'])))
            self.tabella_storico.setItem(riga, 2, QTableWidgetItem(medico_completo))
            self.tabella_storico.setItem(riga, 3, QTableWidgetItem(str(visita['stato'])))

    def salva_modifiche(self):
        """Invia i nuovi dati al controller per fare l'UPDATE (RF7)."""
        nuovi_dati = {
            "email": self.input_email.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "isAgonista": self.check_agonista.isChecked()
        }

        successo = self.gestore_anagrafica.modificaSchedaPaziente(self.cf_paziente, nuovi_dati)
        
        if successo:
            QMessageBox.information(self, "Successo", "Dati anagrafici aggiornati correttamente.")
        else:
            QMessageBox.warning(self, "Errore", "Impossibile aggiornare i dati.")