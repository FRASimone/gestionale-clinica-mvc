from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QTextEdit, QLabel
from controllers.gestore_clinica import GestoreClinica

class DettaglioRefertoDialog(QDialog):
    def __init__(self, id_valutazione: int, parent=None):
        super().__init__(parent)
        self.gestore = GestoreClinica()
        self.id_valutazione = id_valutazione
        self.setWindowTitle("Dettaglio Referto Medico")
        self.resize(400, 300)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        dati = self.gestore.getDettagliValutazione(self.id_valutazione)
        
        if not dati:
            layout.addWidget(QLabel("Errore: Referto non trovato."))
            return

        form = QFormLayout()
        
        # Campi in sola lettura
        anomalie = QTextEdit(dati.get('anomalie', ''))
        anomalie.setReadOnly(True)
        note = QTextEdit(dati.get('noteAggiuntive', ''))
        note.setReadOnly(True)
        overtraining = QTextEdit(dati.get('prevOvertraining', ''))
        overtraining.setReadOnly(True)
        voto = QLabel(str(dati.get('valutazioneClinica', 'N/D')))
        
        form.addRow("Anomalie Riscontrate:", anomalie)
        form.addRow("Prevenzione Overtraining:", overtraining)
        form.addRow("Note Aggiuntive:", note)
        form.addRow("Voto Clinico Finale (1-10):", voto)
        
        layout.addLayout(form)