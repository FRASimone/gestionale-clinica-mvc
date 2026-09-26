from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from controllers.gestore_clinica import GestoreClinica

class CatalogoPrestazioniView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore_clinica = GestoreClinica()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        titolo = QLabel("Aggiungi Nuova Prestazione al Catalogo")
        titolo.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(titolo)

        form_layout = QFormLayout()
        
        self.input_nome_prest = QLineEdit()
        self.input_nome_prest.setPlaceholderText("Es. Visita Ortopedica")
        
        self.input_durata_prest = QLineEdit()
        self.input_durata_prest.setPlaceholderText("Es. 30 (in minuti)")
        
        self.input_costo_prest = QLineEdit()
        self.input_costo_prest.setPlaceholderText("Es. 80.00")
        
        form_layout.addRow("Nome Prestazione:", self.input_nome_prest)
        form_layout.addRow("Durata (Minuti):", self.input_durata_prest)
        form_layout.addRow("Costo (€):", self.input_costo_prest)
        
        layout.addLayout(form_layout)
        
        btn_aggiungi_prest = QPushButton("Salva nel Catalogo")
        btn_aggiungi_prest.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 8px;")
        # chiamata al metodo della view aggiungi prestazione
        btn_aggiungi_prest.clicked.connect(self.handle_aggiungi_prestazione)
        layout.addWidget(btn_aggiungi_prest)
        
        layout.addStretch() # Spinge tutto verso l'alto per un design più pulito

    def handle_aggiungi_prestazione(self):
        """Raccoglie i dati, controlla la validità e chiama il Controller."""
        #raccola di dati
        nome = self.input_nome_prest.text().strip()
        durata_str = self.input_durata_prest.text().strip()
        costo_str = self.input_costo_prest.text().strip()
        
        # Controllo campi vuoti
        if not nome or not durata_str or not costo_str:
            QMessageBox.warning(self, "Errore", "Tutti i campi sono obbligatori.")
            return
            
        # Controllo formato numeri
        try:
            #cosi se l'utente scrive trenta catturo l'errore
            durata = int(durata_str)
            #gli utenti potrebbero scrivere la , per separare ma python usa il .
            costo = float(costo_str.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Errore di formato", "Durata deve essere un intero e Costo un numero valido.")
            return
            
        # Chiamata al Controller Clinico
        successo, messaggio = self.gestore_clinica.aggiungiPrestazione(nome, durata, costo)
        #svuotiamo i campi
        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            self.input_nome_prest.clear()
            self.input_durata_prest.clear()
            self.input_costo_prest.clear()
        else:
            QMessageBox.warning(self, "Errore", messaggio)

# --- BLOCCO DI TEST INDIPENDENTE ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    finestra = CatalogoPrestazioniView()
    finestra.show()
    sys.exit(app.exec())