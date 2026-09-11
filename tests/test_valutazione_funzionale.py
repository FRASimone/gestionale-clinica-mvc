import unittest
from models.valutazione_funzionale import ValutazioneFunzionale

class TestValutazioneFunzionale(unittest.TestCase):
    def setUp(self):
        self.valutazione = ValutazioneFunzionale(
            id_valutazione=1,
            anomalie="Leggera aritmia",
            noteAggiuntive="Da tenere sotto controllo",
            prevOvertraining="Medio",
            valutazioneClinica=7
        )

    def test_aggiorna_note(self):
        self.valutazione.aggiornaNote("Note aggiornate")
        self.assertEqual(self.valutazione.getDettagli()["noteAggiuntive"], "Note aggiornate")

    def test_get_dettagli(self):
        dettagli = self.valutazione.getDettagli()
        self.assertEqual(dettagli["id"], 1)
        self.assertEqual(dettagli["anomalie"], "Leggera aritmia")
        self.assertEqual(dettagli["noteAggiuntive"], "Da tenere sotto controllo")
        self.assertEqual(dettagli["prevOvertraining"], "Medio")
        self.assertEqual(dettagli["valutazioneClinica"], 7)

if __name__ == '__main__':
    unittest.main()
