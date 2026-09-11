import unittest
from models.specializzazione import Specializzazione

class TestSpecializzazione(unittest.TestCase):
    def setUp(self):
        self.specializzazione = Specializzazione(1, "Cardiologia", "Cura del cuore")

    def test_get_nome(self):
        self.assertEqual(self.specializzazione.getNome(), "Cardiologia")

    def test_get_dettagli(self):
        dettagli = self.specializzazione.getDettagli()
        self.assertEqual(dettagli["id"], 1)
        self.assertEqual(dettagli["nome"], "Cardiologia")
        self.assertEqual(dettagli["descrizione"], "Cura del cuore")

if __name__ == '__main__':
    unittest.main()
