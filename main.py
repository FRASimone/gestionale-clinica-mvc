import sys
from PyQt6.QtWidgets import QApplication

# Importiamo l'inizializzatore del DB e la finestra di Login
from database.db_manager import inizializza_database
from database.db_manager import esegui_backup_automatico
from popola_db import popola_database
from views.login_view import LoginWindow 
def avvia_gestionale():
    print("--- [SISTEMA] Avvio Gestionale Clinica ---")
    
    # 1. Controlliamo e inizializziamo il Database per sicurezza
    inizializza_database()
    esegui_backup_automatico()
    popola_database()
    # 2. Avviamo l'applicazione grafica
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Stile moderno multipiattaforma
    
    # 3. Lanciamo la schermata di Login
    finestra_login = LoginWindow()
    finestra_login.show()
    
    # 4. Eseguiamo il loop principale
    sys.exit(app.exec())

if __name__ == "__main__":
    avvia_gestionale()