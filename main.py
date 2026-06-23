import sys
from PyQt6.QtWidgets import QApplication
from views.login_view import LoginWindow

def main():
    # Inizializza l'applicazione PyQt
    app = QApplication(sys.argv)
    
    # Crea e mostra la schermata di login
    finestra_login = LoginWindow()
    finestra_login.show()
    
    # Avvia il loop principale dell'applicazione
    sys.exit(app.exec())

if __name__ == "__main__":
    main()