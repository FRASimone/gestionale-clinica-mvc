from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QTextEdit, 
                             QSpinBox, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

from controllers.gestore_clinica import AccessoNegatoError, GestoreClinica

class ValutazioneFunzionaleView(QWidget):
    # Passiamo l'ID dell'appuntamento direttamente quando apriamo la finestra
    def __init__(self, id_appuntamento: int, id_medico: int):
        super().__init__()
        self.id_medico = id_medico
        self.gestore_clinica = GestoreClinica()
        self.id_appuntamento = id_appuntamento
        
        self.setWindowTitle(f"Valutazione Funzionale - Appuntamento #{self.id_appuntamento}")
        self.resize(500, 550)
        
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        titolo = QLabel("Referto Medico Sportivo")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titolo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titolo)

        form_layout = QFormLayout()

        # 1. Anomalie
        self.input_anomalie = QTextEdit()
        self.input_anomalie.setPlaceholderText("Es: Leggera asimmetria posturale, dolori articolari...")
        self.input_anomalie.setMaximumHeight(80)

        # 2. Prevenzione Overtraining
        self.input_overtraining = QTextEdit()
        self.input_overtraining.setPlaceholderText("Es: Ridurre carico del 20% per 2 settimane, stretching specifico...")
        self.input_overtraining.setMaximumHeight(80)

        # 3. Note Aggiuntive
        self.input_note = QTextEdit()
        self.input_note.setPlaceholderText("Osservazioni cliniche generali...")
        self.input_note.setMaximumHeight(100)

        # 4. Valutazione Clinica Globale (Intero da 1 a 10)
        self.input_valutazione = QSpinBox()
        self.input_valutazione.setRange(1, 10)
        self.input_valutazione.setValue(8) # Valore di default
        self.input_valutazione.setToolTip("Valutazione dello stato di forma da 1 a 10")

        # Aggiungiamo i campi al layout
        form_layout.addRow("Valutazione Clinica (1-10):", self.input_valutazione)
        form_layout.addRow("Anomalie Rilevate:", self.input_anomalie)
        form_layout.addRow("Prev. Overtraining:", self.input_overtraining)
        form_layout.addRow("Note Aggiuntive:", self.input_note)

        layout.addLayout(form_layout)

        # Bottone di salvataggio
        btn_salva = QPushButton("Salva Valutazione e Completa Visita")
        btn_salva.setStyleSheet("background-color: #2E86C1; color: white; font-weight: bold; padding: 10px;")
        btn_salva.clicked.connect(self.handle_salvataggio)
        layout.addWidget(btn_salva)

    def handle_salvataggio(self):
        """Raccoglie i dati, chiama il Controller e gestisce il risultato."""
        
        # Estraiamo i dati inseriti dal Medico
        anomalie = self.input_anomalie.toPlainText().strip()
        overtraining = self.input_overtraining.toPlainText().strip()
        note = self.input_note.toPlainText().strip()
        valutazione = self.input_valutazione.value()

        # Controllo di base (esigiamo almeno le note o le anomalie)
        if not anomalie and not note:
            QMessageBox.warning(self, "Attenzione", "Inserire almeno un'anomalia o una nota aggiuntiva.")
            return

        try:
            successo = self.gestore_clinica.registraValutazioneFunzionale(
            self.id_appuntamento, anomalie, note, overtraining, valutazione,
            id_medico=self.id_medico
        )
        except AccessoNegatoError as e:
            QMessageBox.critical(self, "Accesso Negato", str(e))
            return

        if successo:
            QMessageBox.information(self, "Successo", "Valutazione salvata! L'appuntamento è ora 'Completato'.")
            self.close() # Chiudiamo la finestra del referto
        else:
            QMessageBox.warning(self, "Errore", "Impossibile salvare la valutazione. Verifica il database.")

# --- TEST DIRETTO DELLA VIEW ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Per il test in isolamento, simuliamo di compilare il referto per l'Appuntamento con ID 1
    # Assicurati di aver fatto almeno una prenotazione per far sì che esista l'ID 1 nel database!
    finestra = ValutazioneFunzionaleView(id_appuntamento=1)
    finestra.show()
    sys.exit(app.exec())