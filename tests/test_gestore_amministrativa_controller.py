import io
from contextlib import redirect_stdout

from controller_test_support import ControllerDatabaseTestCase


class TestGestoreAmministrativa(ControllerDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.cf_paziente = self.inserisci_paziente()
        self.id_medico = self.inserisci_dipendente()
        self.id_prestazione = self.inserisci_prestazione("Visita", 30, 80.0)
        self.id_appuntamento = self.inserisci_appuntamento(
            cf_paziente=self.cf_paziente,
            id_medico=self.id_medico,
            id_prestazione=self.id_prestazione,
            stato="Completato",
        )

    def inserisci_pagamento(self, id_appuntamento=None, importo=80.0, data="2026-01-15 10:00:00"):
        if id_appuntamento is None:
            id_appuntamento = self.id_appuntamento
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Pagamento (appuntamento_id, dataOraPagamento, importo, metodo) "
                "VALUES (?, ?, ?, ?)",
                (id_appuntamento, data, importo, "Carta"),
            )
            return cursor.lastrowid

    def test_get_appuntamenti_da_saldare_restituisce_solo_completati_non_pagati(self):
        da_saldare = self.amministrativa.getAppuntamentiDaSaldare(self.cf_paziente)
        self.assertEqual(len(da_saldare), 1)
        self.assertEqual(da_saldare[0]["id"], self.id_appuntamento)
        self.assertEqual(da_saldare[0]["nomePrestazione"], "Visita")
        self.assertEqual(da_saldare[0]["costoBase"], 80.0)

        self.inserisci_pagamento()
        self.assertEqual(self.amministrativa.getAppuntamentiDaSaldare(self.cf_paziente), [])

    def test_verifica_saldo_distigue_pagamento_assente_e_presente(self):
        self.assertFalse(self.amministrativa.verificaSaldoAppuntamento(self.id_appuntamento))
        self.inserisci_pagamento()
        self.assertTrue(self.amministrativa.verificaSaldoAppuntamento(self.id_appuntamento))

    def test_registra_pagamento_persistito_e_blocca_il_doppio_pagamento(self):
        id_pagamento = self.amministrativa.registraPagamento(
            self.id_appuntamento, 80.0, "Contanti"
        )

        self.assertIsNotNone(id_pagamento)
        self.assertIsNone(self.amministrativa.registraPagamento(
            self.id_appuntamento, 80.0, "Contanti"
        ))
        pagamento = self.righe(
            "SELECT appuntamento_id, importo, metodo FROM Pagamento WHERE id = ?",
            (id_pagamento,),
        )[0]
        self.assertEqual(pagamento, {
            "appuntamento_id": self.id_appuntamento,
            "importo": 80.0,
            "metodo": "Contanti",
        })

    def test_emetti_fattura_persistisce_i_dati_e_gestisce_pagamento_assente_o_duplicato(self):
        id_pagamento = self.inserisci_pagamento(importo=92.5)
        self.assertFalse(self.amministrativa.emettiFattura(999, "Email"))

        with redirect_stdout(io.StringIO()) as output:
            emessa = self.amministrativa.emettiFattura(id_pagamento, "Email")

        self.assertTrue(emessa)
        self.assertIn("mario@example.com", output.getvalue())
        fattura = self.righe("SELECT pagamento_id, cf_paziente, totale FROM Fattura")[0]
        self.assertEqual(fattura, {
            "pagamento_id": id_pagamento,
            "cf_paziente": self.cf_paziente,
            "totale": 92.5,
        })
        with redirect_stdout(io.StringIO()):
            duplicata = self.amministrativa.emettiFattura(id_pagamento, "Stampa")
        self.assertFalse(duplicata)

    def test_get_storico_fatture_filtra_paziente_e_ordina_per_data(self):
        id_pagamento_vecchio = self.inserisci_pagamento(data="2026-01-01 10:00:00")
        id_pagamento_recente = self.inserisci_pagamento(
            id_appuntamento=self.inserisci_appuntamento(
                cf_paziente=self.cf_paziente,
                id_medico=self.id_medico,
                id_prestazione=self.id_prestazione,
                data="2026-01-20",
            ),
            data="2026-02-01 10:00:00",
        )
        altro_cf = self.inserisci_paziente(
            "VRDMRC80A01H501Z", "Marco", "Verdi", "marco@example.com", "3330000000"
        )
        id_appuntamento_altro = self.inserisci_appuntamento(
            cf_paziente=altro_cf,
            id_medico=self.id_medico,
            id_prestazione=self.id_prestazione,
            data="2026-01-21",
        )
        id_pagamento_altro = self.inserisci_pagamento(
            id_appuntamento=id_appuntamento_altro,
            data="2026-03-01 10:00:00",
        )
        with self.connessione() as conn:
            conn.executemany(
                "INSERT INTO Fattura "
                "(pagamento_id, cf_paziente, numeroFattura, dataOraEmissione, totale) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (id_pagamento_vecchio, self.cf_paziente, "FATT-OLD", "2026-01-01 10:00:00", 80.0),
                    (id_pagamento_recente, self.cf_paziente, "FATT-NEW", "2026-02-01 10:00:00", 80.0),
                    (id_pagamento_altro, altro_cf, "FATT-OTHER", "2026-03-01 10:00:00", 80.0),
                ],
            )

        storico = self.amministrativa.getStoricoFatturePaziente(self.cf_paziente)
        self.assertEqual([fattura["numeroFattura"] for fattura in storico], ["FATT-NEW", "FATT-OLD"])


if __name__ == "__main__":
    import unittest
    unittest.main()