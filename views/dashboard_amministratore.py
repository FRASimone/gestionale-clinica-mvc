from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Importiamo la View 
from views.reportistica_view import ReportisticaView
from views.registrazione_dipendente import RegistrazioneDipendenteView
from views.gestione_ruoli_view import GestioneRuoliView

class DashboardAmministratore(QWidget):
    def __init__(self, id_admin: int, nome_admin="Amministratore", on_logout=None):
        super().__init__()
        self.id_admin = id_admin
        self.nome_admin = nome_admin
        self.on_logout = on_logout
        
        self.setWindowTitle(f"Gestionale Clinica - Pannello Amministrazione")
        self.resize(1000, 700)
    
        self._build_ui()

    def _build_ui(self):
        layout_principale = QVBoxLayout(self)

        # --- BARRA SUPERIORE (Header) ---
        header_layout = QHBoxLayout()
        
        # Titolo
        titolo = QLabel(f"Pannello di Controllo Direzione - Benvenuto, {self.nome_admin}")
        font = QFont("Arial", 16, QFont.Weight.Bold)
        titolo.setFont(font)
        header_layout.addWidget(titolo)
        
        header_layout.addStretch() # Spinge il bottone di logout a destra
        
        # Bottone di Logout
        btn_logout = QPushButton("Disconnetti")
        btn_logout.setStyleSheet("background-color: #7F8C8D; color: white; padding: 5px 15px; font-weight: bold;")
        btn_logout.clicked.connect(self.esegui_logout)
        header_layout.addWidget(btn_logout)

        layout_principale.addLayout(header_layout)

        # --- SISTEMA A SCHEDE (Tabs) ---
        self.tabs = QTabWidget()
        
        # Aggiungiamo la nostra Reportistica
        self.tabs.addTab(ReportisticaView(), "Area Reportistica e Fatturati")
        
        self.tabs.addTab(RegistrazioneDipendenteView(), "Gestione Dipendenti")
        
        self.tabs.addTab(GestioneRuoliView(id_utente_loggato=self.id_admin), "Gestione Ruoli e Permessi")
        
        layout_principale.addWidget(self.tabs)

    def esegui_logout(self):
        """Gestisce l'uscita dalla sessione e la chiusura della dashboard."""
        risposta = QMessageBox.question(
            self, 
            "Conferma Disconnessione", 
            "Sei sicuro di voler uscire dal pannello di amministrazione?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if risposta == QMessageBox.StandardButton.Yes:
            if self.on_logout:
                self.on_logout()
            self.close()
            # Qui potresti reinizializzare e mostrare la LoginView originaria
            print("--- [SISTEMA] Disconnessione Amministratore effettuata ---")

# --- BLOCCO DI TEST ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    # Applichiamo uno stile generico per renderla più moderna
    app.setStyle("Fusion") 
    
    finestra = DashboardAmministratore(id_admin=1, nome_admin="Admin Supremo")
    finestra.show()
    sys.exit(app.exec())