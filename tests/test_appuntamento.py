import unittest
from models.appuntamento import Appuntamento
from models.paziente import Paziente
from models.dipendente import Medico
from models.prestazione import Prestazione
from models.memo import Memo
from models.valutazione_funzionale import ValutazioneFunzionale

class TestAppuntamento(unittest.TestCase):
    def setUp(self):
        self.paziente = Paziente("RSSMRA80A01H501Z", "Mario", "Rossi", "email@test.com", "1234", False)
        self.medico = Medico(1, "Luigi", "Verdi", "medico@test.com", "pass")
        self.prestazione = Prestazione(1, "Visita", 30, 50.0)
        
        self.appuntamento = Appuntamento(
            id_appuntamento=1,
            data="2023-11-20",
            oraInizio="10:00",
            stato="Confermato",
            paziente=self.paziente,
            medico=self.medico,
            prestazione=self.prestazione
        )

    def test_getters_base(self):
        self.assertEqual(self.appuntamento.getId(), 1)
        self.assertEqual(self.appuntamento.getPaziente(), self.paziente)
        self.assertEqual(self.appuntamento.getPrestazione(), self.prestazione)

    def test_get_dettagli(self):
        dettagli = self.appuntamento.getDettagli()
        self.assertEqual(dettagli["id"], 1)
        self.assertEqual(dettagli["data"], "2023-11-20")
        self.assertEqual(dettagli["oraInizio"], "10:00")
        self.assertEqual(dettagli["stato"], "Confermato")
        self.assertEqual(dettagli["paziente"], self.paziente)
        self.assertEqual(dettagli["medico"], self.medico)
        self.assertEqual(dettagli["prestazione"], self.prestazione)
        self.assertIsNone(dettagli["memo"])
        self.assertIsNone(dettagli["valutazioneFunzionale"])

    def test_calcola_ora_fine(self):
        ora_fine = Appuntamento.calcolaOraFine("10:00", 30)
        self.assertEqual(ora_fine, "10:30")
        
        ora_fine_overflow = Appuntamento.calcolaOraFine("10:45", 30)
        self.assertEqual(ora_fine_overflow, "11:15")

    def test_setters(self):
        self.appuntamento.setStato("Annullato")
        self.assertEqual(self.appuntamento.getDettagli()["stato"], "Annullato")
        
        memo = Memo(id_memo=1, dataInvioProgrammata="2023-11-19")
        self.appuntamento.setMemo(memo)
        self.assertEqual(self.appuntamento.getDettagli()["memo"], memo)
        
        valutazione = ValutazioneFunzionale(1, "Nessuna", "Ok", "Basso", 10)
        self.appuntamento.setValutazioniFunzionali(valutazione)
        self.assertEqual(self.appuntamento.getDettagli()["valutazioneFunzionale"], valutazione)

if __name__ == '__main__':
    unittest.main()
