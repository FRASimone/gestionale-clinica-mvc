from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QCheckBox, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt

from controllers.gestore_anagrafica import GestoreAnagrafica
from controllers.gestore_clinica import GestoreClinica
from controllers.gestore_amministrativa import GestoreAmministrativa
from views.dettaglio_referto_dialog import DettaglioRefertoDialog
from views.cartella_clinica_dialog import CartellaClinicaDialog

class SchedaPazienteView(QWidget):
    def __init__(self, cf_paziente: str, ruolo_utente: str = ""):
        super().__init__()
        self.cf_paziente = cf_paziente
        self.ruolo_utente = ruolo_utente
        self.gestore_anagrafica = GestoreAnagrafica()
        self.gestore_clinica = GestoreClinica()
        self.gestore_admin = GestoreAmministrativa()
        
        self.setWindowTitle(f"Scheda Paziente - Cartella Clinica: {self.cf_paziente}") 
        self.resize(750, 600)
        
        self._build_ui()
        #chiamate per popolare la schermata con i dati
        self._carica_dati_paziente() # legge dal DB e scrive nei campi
        self._carica_storico_clinico()
        self._carica_storico_fatture()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- SEZIONE SUPERIORE: Dati Anagrafici ---
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

        btn_salva = QPushButton("Salva Modifiche Anagrafica")
        btn_salva.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold; padding: 8px;")
        #quando si preme il bottone Salva modifiche si chiama il metodo della view salva
        btn_salva.clicked.connect(self.salva_modifiche)
        layout.addWidget(btn_salva)

        # --- SEZIONE INFERIORE: Storico Clinico e Contabile ---
        titolo_storico = QLabel("Storico Trattamenti e Fatturazione")
        titolo_storico.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px;")
        layout.addWidget(titolo_storico)
        
        # 1. Tabella Storico Medico
        self.tabella_storico = QTableWidget()
        self.tabella_storico.setColumnCount(5)
        self.tabella_storico.setHorizontalHeaderLabels(["Data", "Prestazione", "Medico", "Referto/Stato", "ID_Valutazione"])
        self.tabella_storico.hideColumn(4) #nasconde l'id
        self.tabella_storico.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_storico.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella_storico.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Permette di selezionare un'intera riga
        layout.addWidget(self.tabella_storico)
        
        if self.ruolo_utente == "Medico":
            self.btn_leggi_referto = QPushButton("Leggi Referto (Valutazione Funzionale)")
            self.btn_leggi_referto.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 5px;")
            self.btn_leggi_referto.clicked.connect(self.apri_dettaglio_referto)
            layout.addWidget(self.btn_leggi_referto)
            self.btn_cartella_clinica = QPushButton("Apri Anamnesi")
            self.btn_cartella_clinica.setStyleSheet("background-color: #16A085; color: white; font-weight: bold; padding: 8px;")
            self.btn_cartella_clinica.clicked.connect(self.apri_cartella_clinica)
            layout.addWidget(self.btn_cartella_clinica)
     
        # 2. Tabella Storico Fatture
        titolo_fatture = QLabel("Storico Fatture")
        titolo_fatture.setStyleSheet("font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(titolo_fatture)
        self.tabella_fatture = QTableWidget()
        self.tabella_fatture.setColumnCount(3)
        self.tabella_fatture.setHorizontalHeaderLabels(["N° Fattura", "Data Emissione", "Totale (€)"])
        self.tabella_fatture.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_fatture.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabella_fatture)
        
    def apri_cartella_clinica(self):
        dialog = CartellaClinicaDialog(cf_paziente=self.cf_paziente, ruolo_utente=self.ruolo_utente, parent=self)
        dialog.exec()
        
    def _carica_dati_paziente(self):
        """Richiede al controller i dati attuali per pre-compilare il form."""
        # Usiamo il metodo di ricerca nel gestore Anagrafica
        risultati = self.gestore_anagrafica.ricercaPaziente(self.cf_paziente)
        #utilizziamo poi i risultati per popolare i campi provenienti dal CF
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
        #chiamata al metodo del gestore Clinica per ottenere le visite del paziente
        storico = self.gestore_clinica.getStoricoPaziente(self.cf_paziente)
        
        self.tabella_storico.setRowCount(0)
        
        for riga, visita in enumerate(storico):
            self.tabella_storico.insertRow(riga)
            #prende i dati separati dal dizionario e li fonde in un unica stringa
            medico_completo = f"Dott. {visita['nome_medico']} {visita['cognome_medico']}"
            
            self.tabella_storico.setItem(riga, 0, QTableWidgetItem(str(visita['data'])))
            self.tabella_storico.setItem(riga, 1, QTableWidgetItem(str(visita['nomePrestazione'])))
            self.tabella_storico.setItem(riga, 2, QTableWidgetItem(medico_completo))
            self.tabella_storico.setItem(riga, 3, QTableWidgetItem(str(visita['stato'])))
            #verifica se la visita ha un ID valutazione associato, ovvero se e' stata completata
            id_val = str(visita['id_valutazione']) if visita['id_valutazione'] else ""
            self.tabella_storico.setItem(riga, 4, QTableWidgetItem(id_val))
            #la colonna dell'id e' nascosta, ma recuperabile per aprire il referto collegato
    
    def _carica_storico_fatture(self):
        """Richiede al controller tutte le fatture emesse per il paziente."""
        #anche qui stesso discorso si chiama il gestore Amministrativo per il recupero
        #delle fatture legate al CF
        fatture = self.gestore_admin.getStoricoFatturePaziente(self.cf_paziente)
        
        self.tabella_fatture.setRowCount(0)
        
        for riga, fattura in enumerate(fatture):
            self.tabella_fatture.insertRow(riga)
            
            # Formattiamo il totale per avere sempre due decimali
            totale_formattato = f"{fattura['totale']:.2f} €"
            
            self.tabella_fatture.setItem(riga, 0, QTableWidgetItem(str(fattura['numeroFattura'])))
            self.tabella_fatture.setItem(riga, 1, QTableWidgetItem(str(fattura['dataOraEmissione'])))
            self.tabella_fatture.setItem(riga, 2, QTableWidgetItem(totale_formattato))
    
    def salva_modifiche(self):
        """Invia i nuovi dati al controller per fare l'UPDATE."""
        nuovi_dati = {
            #il metodo legge i dati nei campi in quell'istante e li invia
            "email": self.input_email.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "isAgonista": self.check_agonista.isChecked()
        }
        #chiama il metodo del gestore Anagrafica passando il CF e i nuovi dati per il salvataggio
        successo = self.gestore_anagrafica.modificaSchedaPaziente(self.cf_paziente, nuovi_dati)
        
        if successo:
            QMessageBox.information(self, "Successo", "Dati anagrafici aggiornati correttamente.")
        else:
            QMessageBox.warning(self, "Errore", "Impossibile aggiornare i dati.")
    
    def apri_dettaglio_referto(self):
     riga = self.tabella_storico.currentRow()
     if riga < 0:
         QMessageBox.warning(self, "Attenzione", "Seleziona una visita dallo storico.")
         return

     stato = self.tabella_storico.item(riga, 3).text()
     if stato != "Completato":
         QMessageBox.information(self, "Info", "Nessun referto disponibile. La visita non è ancora stata completata.")
         return

     # Estraiamo l'ID nascosto
     id_val_testo = self.tabella_storico.item(riga, 4).text()
     if id_val_testo:
        dialog = DettaglioRefertoDialog(int(id_val_testo), ruolo_utente=self.ruolo_utente, parent=self)
        dialog.exec()
     else:
         QMessageBox.warning(self, "Errore", "Referto non trovato nel database.")