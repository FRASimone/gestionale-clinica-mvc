import unittest
from models.prestazione import Prestazione

class TestPrestazione(unittest.TestCase):
    def setUp(self):
        # Questo metodo viene eseguito prima di ogni test
        self.prestazione = Prestazione(id_prestazione=1, nomePrestazione="Visita Cardiologica", durataMinuti=30, costoBase=80.0)

    def test_get_costo(self):
        self.assertEqual(self.prestazione.getCosto(), 80.0)

    def test_get_durata(self):
        self.assertEqual(self.prestazione.getDurata(), 30)

    def test_get_info_prestazione(self):
        expected_info = {
            "id": 1,
            "nomePrestazione": "Visita Cardiologica",
            "durataMinuti": 30,
            "costoBase": 80.0
        }
        self.assertEqual(self.prestazione.getInfoPrestazione(), expected_info)

if __name__ == '__main__':
    unittest.main()
