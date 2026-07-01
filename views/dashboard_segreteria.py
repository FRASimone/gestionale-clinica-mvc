from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFormLayout, QMessageBox, QCheckBox, QTabWidget)
from PyQt6.QtCore import Qt

# Importiamo il Controller per passargli i comandi
from controllers.gestore_anagrafica import GestoreAnagrafica
from views.prenotazione_view import PrenotazioneView
from views.scheda_paziente_view import SchedaPazienteView
from views.catalogo_prestazioni_view import CatalogoPrestazioniView
from controllers.gestore_clinica import GestoreClinica
from views.gestione_amministrativa_view import GestioneAmministrativaView

class DashboardSegreteria(QWidget):
    def __init__(self, utente_loggato):
        super().__init__()
        self.utente_loggato = utente_loggato # Riceviamo l'oggetto del dipendente dal login
        self.gestore = GestoreAnagrafica() # Istanziamo il nostro "motore"
        self.gestore_clinica = GestoreClinica()
        
        self.setWindowTitle(f"Area Segreteria - {self.utente_loggato.getInfo()}")
        self.resize(800, 600)
        
        self._build_ui()

    def _build_ui(self):
        layout_principale = QVBoxLayout(self)
        
       # --- BARRA SUPERIORE (Titolo + Bottone Memo) ---
        header_layout = QHBoxLayout()
        
        titolo = QLabel("Pannello di Controllo Segreteria")
        font = titolo.font()
        font.setPointSize(16)
        font.setBold(True)
        titolo.setFont(font)
        header_layout.addWidget(titolo)
        
        header_layout.addStretch() # Spinge il bottone tutto a destra
        
        self.btn_memo = QPushButton("Forza Invio Memo")
        self.btn_memo.setStyleSheet("background-color: #F1C40F; color: black; font-weight: bold; padding: 8px;")
        self.btn_memo.clicked.connect(self.lancia_promemoria)
        header_layout.addWidget(self.btn_memo)
        
        layout_principale.addLayout(header_layout)
        # -----------------------------------------------

        # Sistema a Schede (Tabs)
        tabs = QTabWidget()
        tabs.addTab(self._tab_nuovo_paziente(), "Registra Nuovo Paziente")
        tabs.addTab(self._tab_ricerca_pazienti(), "Cerca Pazienti")
        tabs.addTab(PrenotazioneView(), "Prenota Appuntamento") 
        tabs.addTab(CatalogoPrestazioniView(), "Catalogo Prestazioni")
        tabs.addTab(GestioneAmministrativaView(), "Cassa e Fatturazione")

        layout_principale.addWidget(tabs)
    
    def lancia_promemoria(self):
        """Richiama il batch del Controller e avvisa l'utente."""
        # Esegue il print nel terminale
        self.gestore_clinica.inviaPromemoriaAutomatici() 
        
        # Mostra un pop-up per confermare che l'azione è partita
        QMessageBox.information(
            self, 
            "Procedura Completata", 
            "I promemoria per gli appuntamenti di domani sono stati elaborati.\nControlla il terminale per gli invii."
        )

    # --- COSTRUZIONE DELLA PRIMA SCHEDA ---
    def _tab_nuovo_paziente(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        form_layout = QFormLayout()
        
        self.input_cf = QLineEdit()
        self.input_nome = QLineEdit()
        self.input_cognome = QLineEdit()
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
        
        btn_aggiungi = QPushButton("Salva Paziente")
        btn_aggiungi.clicked.connect(self.handle_aggiungi_paziente)
        layout.addWidget(btn_aggiungi)
        
        layout.addStretch() # Spinge gli elementi verso l'alto
        return widget

    # --- COSTRUZIONE DELLA SECONDA SCHEDA ---
    def _tab_ricerca_pazienti(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Barra di ricerca orizzontale
        layout_ricerca = QHBoxLayout()
        self.input_ricerca = QLineEdit()
        self.input_ricerca.setPlaceholderText("Cerca per CF o Cognome e premi Cerca...")
        btn_cerca = QPushButton("Cerca")
        btn_cerca.clicked.connect(self.handle_ricerca)
        
        layout_ricerca.addWidget(self.input_ricerca)
        layout_ricerca.addWidget(btn_cerca)
        layout.addLayout(layout_ricerca)
        
        # Tabella visiva per i risultati
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(6)
        self.tabella.setHorizontalHeaderLabels(["CF", "Nome", "Cognome", "Email", "Telefono", "Agonista"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabella)
        self.btn_apri_scheda = QPushButton("Apri Cartella Paziente Selezionato")
        self.btn_apri_scheda.setStyleSheet("background-color: #9B59B6; color: white; padding: 10px;")
        self.btn_apri_scheda.clicked.connect(self.apri_scheda_segreteria)
        layout.addWidget(self.btn_apri_scheda)
        
        return widget

    # =================================================================
    # LOGICA DI COLLEGAMENTO (La View chiede al Controller di agire)
    # =================================================================

    def handle_aggiungi_paziente(self):
        """Prende i dati dal form e li passa al Gestore."""
        cf = self.input_cf.text().strip()
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        telefono = self.input_telefono.text().strip()
        is_agonista = self.check_agonista.isChecked()
        
        if not cf or not nome or not cognome:
            QMessageBox.warning(self, "Errore", "CF, Nome e Cognome sono obbligatori.")
            return
            
        # CHIAMATA AL METODO CHE HAI SCRITTO PRIMA
        nuovo_paziente = self.gestore.aggiungiPaziente(cf, nome, cognome, email, telefono, is_agonista)
        
        if nuovo_paziente:
            QMessageBox.information(self, "Successo", "Paziente registrato correttamente!")
            # Svuota i campi dopo il salvataggio
            self.input_cf.clear()
            self.input_nome.clear()
            self.input_cognome.clear()
            self.input_email.clear()
            self.input_telefono.clear()
            self.check_agonista.setChecked(False)
        else:
            QMessageBox.critical(self, "Errore", "Errore nell'inserimento. Il CF potrebbe essere già presente.")

    def handle_ricerca(self):
        """Passa il parametro al Gestore e riempie la tabella con i risultati."""
        parametro = self.input_ricerca.text().strip()
        
        # CHIAMATA AL METODO CHE HAI SCRITTO PRIMA
        risultati = self.gestore.ricercaPaziente(parametro)
        
        self.tabella.setRowCount(0) # Svuota la tabella da ricerche precedenti
        
        if not risultati:
            QMessageBox.information(self, "Ricerca", "Nessun paziente trovato.")
            return
            
        # Popoliamo la tabella riga per riga
        self.tabella.setRowCount(len(risultati))
        for row_idx, paziente in enumerate(risultati):
            
            # Usiamo il metodo del Model Paziente per avere un dizionario pulito
            dati = paziente.getDatiPaziente() 
            
            self.tabella.setItem(row_idx, 0, QTableWidgetItem(dati["cf"]))
            self.tabella.setItem(row_idx, 1, QTableWidgetItem(dati["nome"]))
            self.tabella.setItem(row_idx, 2, QTableWidgetItem(dati["cognome"]))
            self.tabella.setItem(row_idx, 3, QTableWidgetItem(dati["email"]))
            self.tabella.setItem(row_idx, 4, QTableWidgetItem(dati["telefono"]))
            
            # Traduciamo il True/False in Sì/No per l'interfaccia
            agonista_str = "Sì" if dati["isAgonista"] else "No"
            self.tabella.setItem(row_idx, 5, QTableWidgetItem(agonista_str))
    
    def apri_scheda_segreteria(self):
        riga = self.tabella.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un paziente dalla tabella.")
            return
            
        cf_selezionato = self.tabella.item(riga, 0).text() # Il CF è nella colonna 0
        self.finestra_scheda = SchedaPazienteView(cf_paziente=cf_selezionato)
        self.finestra_scheda.show()
            
        # --- TEST DIRETTO DELLA VIEW ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
            
    # Creiamo una finta classe Dipendente solo per non far crashare la View nel test
    class MockDipendente:
        def __init__(self):
            self.nome = "Mario"
            self.cognome = "Rossi"
            self.ruolo = "Segretario"
                    
        def getInfo(self):
            return f"{self.nome} {self.cognome} ({self.ruolo})"

    app = QApplication(sys.argv)
            
    utente_finto = MockDipendente()
    finestra = DashboardSegreteria(utente_loggato=utente_finto)
    finestra.show()
            
    sys.exit(app.exec())