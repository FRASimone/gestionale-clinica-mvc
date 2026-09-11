import unittest
from unittest.mock import patch, MagicMock
from controllers.gestore_reportistica import GestoreReportistica
import json

class TestGestoreReportistica(unittest.TestCase):
    def setUp(self):
        self.gestore = GestoreReportistica("test_db.db")

    @patch('controllers.gestore_reportistica.sqlite3.connect')
    def test_genera_report_pazienti(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock result of COUNT query
        mock_cursor.fetchone.return_value = {"totale_pazienti": 50}
        mock_cursor.lastrowid = 1

        report = self.gestore.generaReportPazienti(2023, 11)

        self.assertEqual(report.getDatiReport()["id"], 1)
        self.assertEqual(report.getDatiReport()["datiAggregati"]["totale_pazienti_visitati"], 50)
        self.assertEqual(mock_cursor.execute.call_count, 2) # SELECT and INSERT

    @patch('controllers.gestore_reportistica.sqlite3.connect')
    def test_visualizza_report(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate JSON data from DB
        dati = {"fatturato": 1000}
        dati_json = json.dumps(dati)
        
        mock_cursor.fetchone.return_value = {
            "id": 1, 
            "annoRiferimento": 2023, 
            "meseRiferimento": 11,
            "tipoReport": "Test",
            "datiAggregati": dati_json
        }

        risultato = self.gestore.visualizzaReport(1)

        self.assertIsNotNone(risultato)
        self.assertEqual(risultato["id"], 1)
        self.assertEqual(risultato["datiAggregati"]["fatturato"], 1000)

if __name__ == '__main__':
    unittest.main()
