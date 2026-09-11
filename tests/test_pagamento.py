import unittest
from datetime import datetime
from models.pagamento import Pagamento
from models.appuntamento import Appuntamento
from models.fattura import Fattura

class TestPagamento(unittest.TestCase):
    def setUp(self):
        self.data_pagamento = datetime(2023, 11, 20, 10, 45)
        self.pagamento = Pagamento(1, self.data_pagamento, 50.0, "Carta di Credito")

    def test_getters_base(self):
        self.assertEqual(self.pagamento.getId(), 1)
        self.assertEqual(self.pagamento.getDataOraPagamento(), self.data_pagamento)
        self.assertEqual(self.pagamento.getImporto(), 50.0)
        self.assertEqual(self.pagamento.getMetodo(), "Carta di Credito")
        self.assertIsNone(self.pagamento.getAppuntamento())
        self.assertIsNone(self.pagamento.getFattura())

    def test_setters_e_get_dettagli(self):
        # Usiamo stringhe mock per appuntamento e fattura per semplicità
        mock_appuntamento = "Appuntamento1"
        mock_fattura = "Fattura1"
        
        self.pagamento.setAppuntamento(mock_appuntamento)
        self.pagamento.setFattura(mock_fattura)
        
        dettagli = self.pagamento.getDettagliTransazione()
        self.assertEqual(dettagli["appuntamento"], mock_appuntamento)
        self.assertEqual(dettagli["fattura"], mock_fattura)

if __name__ == '__main__':
    unittest.main()
