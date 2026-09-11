import unittest
from unittest.mock import patch, MagicMock
from controllers.gestore_anagrafica import GestoreAnagrafica

class TestGestoreAnagrafica(unittest.TestCase):
    def setUp(self):
        # Inizializziamo il gestore con un db fittizio, ma lo mockeremo comunque.
        self.gestore = GestoreAnagrafica("test_db.db")

    @patch('controllers.gestore_anagrafica.sqlite3.connect')
    def test_registra_dipendente_password_invalida(self, mock_connect):
        # Test password corta
        success, msg = self.gestore.registraDipendente("Mario", "Rossi", "email", "123", "Medico")
        self.assertFalse(success)
        self.assertIn("almeno 8 caratteri", msg)

        # Test password senza numeri
        success, msg = self.gestore.registraDipendente("Mario", "Rossi", "email", "password", "Medico")
        self.assertFalse(success)
        self.assertIn("almeno una lettera e un numero", msg)

    @patch('controllers.gestore_anagrafica.sqlite3.connect')
    def test_registra_dipendente_successo(self, mock_connect):
        # Configuriamo il mock della connessione e del cursore
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        success, msg = self.gestore.registraDipendente("Mario", "Rossi", "mario@email.com", "Password123", "Medico")
        
        # Verifichiamo che il metodo sqlite3.connect sia stato chiamato
        mock_connect.assert_called_once_with("test_db.db")
        # Verifichiamo che la execute del cursor sia stata chiamata coi parametri giusti
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        self.assertIn("INSERT INTO Dipendente", args[0])
        self.assertEqual(args[1], ("Mario", "Rossi", "mario@email.com", "Password123", "Medico"))
        
        # Verifichiamo il commit e la chiusura della connessione
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
        self.assertTrue(success)
        self.assertIn("Registrazione completata", msg)

    @patch('controllers.gestore_anagrafica.sqlite3.connect')
    def test_cerca_utente_per_email_trovato(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simuliamo che il database restituisca una riga
        mock_row = {"id": 1, "nome": "Mario", "cognome": "Rossi", "email": "mario@email.com", "password": "Password123", "ruolo": "Medico"}
        mock_cursor.fetchone.return_value = mock_row
        
        risultato = self.gestore.cercaUtentePerEmail("mario@email.com")
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM Dipendente WHERE email = ?", ("mario@email.com",))
        self.assertIsNotNone(risultato)
        self.assertEqual(risultato["nome"], "Mario")

if __name__ == '__main__':
    unittest.main()
