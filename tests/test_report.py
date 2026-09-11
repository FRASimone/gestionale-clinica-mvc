import unittest
from models.report import Report

class TestReport(unittest.TestCase):
    def setUp(self):
        self.dati = {"totale_incassi": 5000, "numero_visite": 100}
        self.report = Report(1, 2023, 11, "Mensile", self.dati)

    def test_get_dati_report(self):
        dati_report = self.report.getDatiReport()
        self.assertEqual(dati_report["id"], 1)
        self.assertEqual(dati_report["annoRiferimento"], 2023)
        self.assertEqual(dati_report["meseRiferimento"], 11)
        self.assertEqual(dati_report["tipoReport"], "Mensile")
        self.assertEqual(dati_report["datiAggregati"], self.dati)

if __name__ == '__main__':
    unittest.main()
