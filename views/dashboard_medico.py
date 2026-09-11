from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Importiamo la View dell'agenda già pronta
from views.agenda_medico_view import AgendaMedicoView
from views.ricerca_pazienti_view import RicercaPazientiView

class DashboardMedico(QWidget):
    def __init__(self, id_medico: int = 1, nome_medico: str = "Rossi"):
        super().__init__()
        self.id_medico = id_medico
        self.nome_medico = nome_medico
        
        self.setWindowTitle(f"Gestionale Clinica - Area Medica")
        self.resize(1000, 700)
        
        self._build_ui()
        self._inizializza_sessione_medico()

    def _build_ui(self):
        layout_principale = QVBoxLayout(self)

        # --- BARRA SUPERIORE (Header di Sessione) ---
        header_layout = QHBoxLayout()
        
        # Titolo e Benvenuto
        titolo = QLabel(f"Pannello Medico - Dott. {self.nome_medico}")
        font = QFont("Arial", 16, QFont.Weight.Bold)
        titolo.setFont(font)
        header_layout.addWidget(titolo)
        
        header_layout.addStretch() 
        
        # Bottone di Logout
        btn_logout = QPushButton("Disconnetti")
        btn_logout.setStyleSheet("background-color: #7F8C8D; color: white; padding: 5px 15px; font-weight: bold;")
        btn_logout.clicked.connect(self.esegui_logout)
        header_layout.addWidget(btn_logout)

        layout_principale.addLayout(header_layout)

        # --- SISTEMA A SCHEDE (Tabs) ---
        self.tabs = QTabWidget()
        
        # Istanziamo la vista dell'agenda
        self.view_agenda = AgendaMedicoView(ruolo_utente="Medico")
        
        # Inseriamo l'agenda come Tab principale
        self.tabs.addTab(self.view_agenda, "Agenda Appuntamenti e Visite")
        self.tabs.addTab(RicercaPazientiView(ruolo_utente="Medico"), "Ricerca Pazienti")
        
        layout_principale.addWidget(self.tabs)

    def _inizializza_sessione_medico(self):
        """
        Ottimizzazione UX: Seleziona automaticamente il medico loggato 
        nella tendina dell'agenda per evitare selezioni manuali errate.
        """
        index = self.view_agenda.combo_medico.findData(self.id_medico)
        if index >= 0:
            self.view_agenda.combo_medico.setCurrentIndex(index)
            self.view_agenda.combo_medico.setEnabled(False)
            # Carica direttamente l'agenda del giorno per il medico corrente
            # (mostra_avviso=False: è un caricamento automatico, non deve
            # aprire popup se l'agenda del giorno è vuota)
            self.view_agenda.carica_appuntamenti(mostra_avviso=False)

    def esegui_logout(self):
        """Gestisce la disconnessione sicura dall'area medica."""
        risposta = QMessageBox.question(
            self, 
            "Conferma Uscita", 
            "Sei sicuro di voler chiudere la sessione di lavoro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if risposta == QMessageBox.StandardButton.Yes:
            self.close()
            print(f"--- [SISTEMA] Sessione terminata per il Dott. {self.nome_medico} ---")

# --- BLOCCO DI TEST AUTONOMO ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    # Simuliamo l'accesso del Medico con ID 2 (deve corrispondere a un ID esistente nel DB per caricare i dati)
    finestra = DashboardMedico(id_medico=7, nome_medico="Stefano Goat")
    finestra.show()
    sys.exit(app.exec())