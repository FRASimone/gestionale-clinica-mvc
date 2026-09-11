import unittest
from datetime import datetime
from models.fattura import Fattura
from models.paziente import Paziente

class TestFattura(unittest.TestCase):
    def setUp(self):
        self.paziente = Paziente("RSSMRA80A01H501Z", "Mario", "Rossi", "email@test.com", "1234", False)
        self.data_emissione = datetime(2023, 11, 20, 10, 30)
        self.fattura = Fattura(1, "FATT-001", self.data_emissione, 100.0, self.paziente)

    def test_getters(self):
        self.assertEqual(self.fattura.getId(), 1)
        self.assertEqual(self.fattura.getNumeroFattura(), "FATT-001")
        self.assertEqual(self.fattura.getDataOraEmissione(), self.data_emissione)
        self.assertEqual(self.fattura.getTotale(), 100.0)
        self.assertEqual(self.fattura.getPaziente(), self.paziente)

    def test_get_dati_fiscale(self):
        dati = self.fattura.getDatiFiscale()
        self.assertEqual(dati["id"], 1)
        self.assertEqual(dati["numeroFattura"], "FATT-001")
        self.assertEqual(dati["dataOraEmissione"], self.data_emissione)
        self.assertEqual(dati["totale"], 100.0)
        self.assertEqual(dati["paziente"], self.paziente)

if __name__ == '__main__':
    unittest.main()
