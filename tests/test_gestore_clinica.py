import unittest
from unittest.mock import patch, MagicMock
from datetime import date, time
from controllers.gestore_clinica import GestoreClinica, AccessoNegatoError

class TestGestoreClinica(unittest.TestCase):
    def setUp(self):
        self.gestore = GestoreClinica("test_db.db")

    @patch('controllers.gestore_clinica.sqlite3.connect')
    def test_aggiorna_anamnesi_medico(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula cartella clinica inesistente per inserire
        mock_cursor.fetchone.return_value = None

        result = self.gestore.aggiornaAnamnesi("RSSMRA80A01H501Z", "Tutto ok", "Medico")
        self.assertTrue(result)
        self.assertEqual(mock_cursor.execute.call_count, 2) # 1 for SELECT, 1 for INSERT

    def test_aggiorna_anamnesi_accesso_negato(self):
        with self.assertRaises(AccessoNegatoError):
            self.gestore.aggiornaAnamnesi("RSSMRA80A01H501Z", "Tutto ok", "Segretario")

    @patch('controllers.gestore_clinica.sqlite3.connect')
    def test_crea_appuntamento(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # mock_cursor.fetchone deve restituire prima la durata della prestazione
        # poi le fetchall successive (per i conflitti) devono restituire liste vuote
        mock_cursor.fetchone.return_value = {"durataMinuti": 30}
        mock_cursor.fetchall.return_value = []

        success, msg = self.gestore.creaAppuntamento(
            date(2023, 11, 20), 
            time(10, 0), 
            "RSSMRA80A01H501Z", 
            1, 
            1
        )
        
        self.assertTrue(success)
        self.assertIn("confermato", msg)
        # execute called: SELECT durata, SELECT conflitti_medico, SELECT conflitti_paziente, INSERT
        self.assertEqual(mock_cursor.execute.call_count, 4)

if __name__ == '__main__':
    unittest.main()
