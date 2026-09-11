import unittest
from models.paziente import Paziente
from models.cartella_clinica import CartellaClinica
from datetime import date

class TestPaziente(unittest.TestCase):
    def setUp(self):
        self.paziente = Paziente(
            cf="RSSMRA80A01H501Z",
            nome="Mario",
            cognome="Rossi",
            email="mario.rossi@email.com",
            telefono="3331234567",
            is_agonista=False
        )

    def test_get_cf(self):
        self.assertEqual(self.paziente.getCf(), "RSSMRA80A01H501Z")

    def test_get_dati_paziente(self):
        expected_dati = {
            "cf": "RSSMRA80A01H501Z",
            "nome": "Mario",
            "cognome": "Rossi",
            "email": "mario.rossi@email.com",
            "telefono": "3331234567",
            "isAgonista": False
        }
        self.assertEqual(self.paziente.getDatiPaziente(), expected_dati)

    def test_set_stato_agonista(self):
        self.paziente.setStatoAgonista(True)
        self.assertTrue(self.paziente.getDatiPaziente()["isAgonista"])

    def test_aggiorna_dati(self):
        nuovi_dati = {"email": "nuova@email.com", "telefono": "111222333"}
        self.assertTrue(self.paziente.aggiornaDati(nuovi_dati))
        
        dati_aggiornati = self.paziente.getDatiPaziente()
        self.assertEqual(dati_aggiornati["email"], "nuova@email.com")
        self.assertEqual(dati_aggiornati["telefono"], "111222333")

    def test_gestione_cartella_clinica(self):
        self.assertIsNone(self.paziente.getCartellaClinica())
        cartella = CartellaClinica(1, date(2023, 1, 1), "Nessuna patologia pregressa")
        self.paziente.setCartellaClinica(cartella)
        self.assertEqual(self.paziente.getCartellaClinica(), cartella)

    def test_gestione_fatture(self):
        self.assertEqual(len(self.paziente.getListaFatture()), 0)
        self.paziente.aggiungiFattura("Fattura1")
        self.assertEqual(self.paziente.getListaFatture(), ["Fattura1"])

if __name__ == '__main__':
    unittest.main()
