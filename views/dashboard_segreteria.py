from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFormLayout, QMessageBox, QCheckBox, QTabWidget)
from PyQt6.QtCore import Qt

# Importiamo il Controller per passargli i comandi
from views.registrazione_paziente_view import RegistrazionePazienteView
from controllers.gestore_anagrafica import GestoreAnagrafica
from views.prenotazione_view import PrenotazioneView
from views.ricerca_pazienti_view import RicercaPazientiView
from views.scheda_paziente_view import SchedaPazienteView
from views.catalogo_prestazioni_view import CatalogoPrestazioniView
from controllers.gestore_clinica import GestoreClinica
from views.gestione_amministrativa_view import GestioneAmministrativaView
from views.gestione_appuntamenti_segreteria_view import GestioneAppuntamentiSegreteriaView

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
        # Bottone dei Promemoria
        self.btn_memo = QPushButton("Forza Invio Memo")
        self.btn_memo.setStyleSheet("background-color: #F1C40F; color: black; font-weight: bold; padding: 8px;")
        #bottone della view per la simulazione del promemoria
        self.btn_memo.clicked.connect(self.lancia_promemoria)
        header_layout.addWidget(self.btn_memo)
        
        # BOTTONE DISCONNETTI 
        self.btn_logout = QPushButton("Disconnetti")
        self.btn_logout.setStyleSheet("background-color: #7F8C8D; color: white; padding: 8px 15px; font-weight: bold;")
        self.btn_logout.clicked.connect(self.esegui_logout)
        header_layout.addWidget(self.btn_logout)
        
        layout_principale.addLayout(header_layout)
        # -----------------------------------------------

        # Sistema a Schede (Tabs)
        tabs = QTabWidget()
        tabs.addTab(RegistrazionePazienteView(), "Registra Nuovo Paziente")
        tabs.addTab(RicercaPazientiView(ruolo_utente="Segretario"), "Cerca Pazienti")
        tabs.addTab(PrenotazioneView(), "Prenota Appuntamento") 
        tabs.addTab(GestioneAppuntamentiSegreteriaView(), "Gestione e Modifica Appuntamenti")
        tabs.addTab(CatalogoPrestazioniView(), "Catalogo Prestazioni")
        tabs.addTab(GestioneAmministrativaView(), "Cassa e Fatturazione")

        layout_principale.addWidget(tabs)
    
    def lancia_promemoria(self):
        """Richiama il Controller e avvisa l'utente."""
        # Esegue il print nel terminale, chiamata del gestore Clinica
        conteggio = self.gestore_clinica.inviaPromemoriaAutomatici() 
        
        if conteggio == -1:
            QMessageBox.critical(self, "Errore", "Si è verificato un errore durante l'invio dei promemoria.\nControlla il terminale per i dettagli.")
        elif conteggio == 0:
            QMessageBox.information(self, "Nessun Promemoria da Inviare", "Non ci sono appuntamenti di domani in attesa di notifica.")
        else:
            QMessageBox.information(
                self, 
                "Procedura Completata", 
                f"{conteggio} promemoria inviati con successo.\nControlla il terminale per i dettagli."
            )
        
        
    def esegui_logout(self):
        """Gestisce l'uscita dalla sessione e la chiusura della dashboard."""
        risposta = QMessageBox.question(
            self, 
            "Conferma Disconnessione", 
            "Sei sicuro di voler uscire dal pannello di segreteria?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if risposta == QMessageBox.StandardButton.Yes:
            self.close()
            print(f"--- [SISTEMA] Disconnessione effettuata per: {self.utente_loggato.getInfo()} ---")
            
    
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