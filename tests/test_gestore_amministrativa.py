import unittest
from unittest.mock import patch, MagicMock
from controllers.gestore_amministrativa import GestoreAmministrativa

class TestGestoreAmministrativa(unittest.TestCase):
    def setUp(self):
        self.gestore = GestoreAmministrativa("test_db.db")

    @patch('controllers.gestore_amministrativa.sqlite3.connect')
    def test_get_appuntamenti_da_saldare(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {"id": 1, "data": "2023-11-20", "nomePrestazione": "Visita", "costoBase": 50.0}
        ]

        risultati = self.gestore.getAppuntamentiDaSaldare("RSSMRA80A01H501Z")

        mock_cursor.execute.assert_called_once()
        self.assertEqual(len(risultati), 1)
        self.assertEqual(risultati[0]["costoBase"], 50.0)

    @patch('controllers.gestore_amministrativa.sqlite3.connect')
    def test_registra_pagamento(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock verificaSaldoAppuntamento to return False (non pagato)
        # We need to mock fetchone to return None first, for verificaSaldoAppuntamento
        # But wait, verificaSaldoAppuntamento creates its own connection and cursor.
        # Since sqlite3.connect is patched at module level, BOTH connections will use the same mock.
        
        # When verificaSaldoAppuntamento calls fetchone(), it should return None.
        # The second execute is the INSERT.
        # We can use side_effect for fetchone if needed, but since verificaSaldoAppuntamento
        # only needs fetchone, and registraPagamento doesn't use fetchone, we just set fetchone.return_value = None
        mock_cursor.fetchone.return_value = None
        mock_cursor.lastrowid = 10

        risultato = self.gestore.registraPagamento(1, 50.0, "Contanti")

        # Verifica che sia stata eseguita la verifica
        self.assertEqual(mock_cursor.execute.call_count, 2)
        self.assertEqual(risultato, 10)

if __name__ == '__main__':
    unittest.main()
