from PyQt6.QtWidgets import QDialog, QVBoxLayout
from views.registrazione_paziente_view import RegistrazionePazienteView

class RegistrazionePazienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrazione Rapida Nuovo Paziente")
        self.resize(350, 300)
        
        layout = QVBoxLayout(self)
        
        # Inseriamo il Widget creato al Passo 1 all'interno del Dialog
        self.registrazione_view = RegistrazionePazienteView()
        
        # Quando il widget salva il paziente, chiudiamo il popup e restituiamo 'Accepted'
        self.registrazione_view.paziente_salvato.connect(self._paziente_aggiunto)
        
        layout.addWidget(self.registrazione_view)

    def _paziente_aggiunto(self, cf):
        """Metodo chiamato dal segnale quando il salvataggio va a buon fine."""
        # Memorizziamo il CF per poterlo leggere dalla vista chiamante
        self.cf_creato = cf 
        self.accept()