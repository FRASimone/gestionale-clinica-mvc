import unittest

from models.appuntamento import Appuntamento
from models.paziente import Paziente


class TestAppuntamento(unittest.TestCase):
    def test_calcola_ora_fine_attraversa_mezzanotte(self):
        self.assertEqual(Appuntamento.calcolaOraFine("23:45", 30), "00:15")

    def test_calcola_ora_fine_rifiuta_orario_non_valido(self):
        with self.assertRaises(ValueError):
            Appuntamento.calcolaOraFine("25:00", 30)


class TestPaziente(unittest.TestCase):
    def setUp(self):
        self.paziente = Paziente(
            "RSSMRA80A01H501Z",
            "Mario",
            "Rossi",
            "mario@example.com",
            "3331234567",
            False,
        )

    def test_aggiorna_dati_parziali_senza_modificare_campi_non_supportati(self):
        risultato = self.paziente.aggiornaDati({
            "email": "nuova@example.com",
            "nome": "Nome ignorato",
            "campo_sconosciuto": "valore ignorato",
        })

        self.assertTrue(risultato)
        self.assertEqual(self.paziente.getDatiPaziente(), {
            "cf": "RSSMRA80A01H501Z",
            "nome": "Mario",
            "cognome": "Rossi",
            "email": "nuova@example.com",
            "telefono": "3331234567",
            "isAgonista": False,
        })

    def test_aggiorna_dati_payload_non_valido_non_modifica_il_paziente(self):
        dati_iniziali = self.paziente.getDatiPaziente().copy()

        self.assertFalse(self.paziente.aggiornaDati(None))
        self.assertEqual(self.paziente.getDatiPaziente(), dati_iniziali)


if __name__ == "__main__":
    unittest.main()