import unittest
from datetime import date
from models.cartella_clinica import CartellaClinica
from models.valutazione_funzionale import ValutazioneFunzionale

class TestCartellaClinica(unittest.TestCase):
    def setUp(self):
        self.cartella = CartellaClinica(
            id_cartella=1,
            dataCreazione=date(2023, 10, 1),
            anamnesiGenerica="Paziente in buona salute"
        )
        self.valutazione = ValutazioneFunzionale(
            id_valutazione=1,
            anomalie="Nessuna",
            noteAggiuntive="Tutto ok",
            prevOvertraining="Basso",
            valutazioneClinica=8
        )

    def test_get_id(self):
        self.assertEqual(self.cartella.getId(), 1)

    def test_get_data_creazione(self):
        self.assertEqual(self.cartella.getDataCreazione(), date(2023, 10, 1))

    def test_get_anamnesi_generica(self):
        self.assertEqual(self.cartella.getAnamnesiGenerica(), "Paziente in buona salute")

    def test_aggiorna_anamnesi(self):
        self.cartella.aggiornaAnamnesi("Paziente con lieve ipertensione")
        self.assertEqual(self.cartella.getAnamnesiGenerica(), "Paziente con lieve ipertensione")

    def test_aggiungi_valutazione(self):
        self.assertEqual(len(self.cartella.getValutazioni()), 0)
        self.cartella.aggiungiValutazione(self.valutazione)
        self.assertEqual(len(self.cartella.getValutazioni()), 1)
        self.assertEqual(self.cartella.getValutazioni()[0], self.valutazione)

if __name__ == '__main__':
    unittest.main()
