import io
from contextlib import redirect_stdout

from controller_test_support import ControllerDatabaseTestCase


class TestGestoreReportistica(ControllerDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.cf_mario = self.inserisci_paziente()
        self.cf_sara = self.inserisci_paziente(
            "SRANNA85C41H501X", "Sara", "Neri", "sara@example.com", "3331111111"
        )
        self.id_medico_luca = self.inserisci_dipendente()
        self.id_medico_sara = self.inserisci_dipendente(
            "Sofia", "Neri", "sofia@example.com", "Password123", "Medico"
        )
        self.id_visita = self.inserisci_prestazione("Visita", 30, 100.0)
        self.id_fisioterapia = self.inserisci_prestazione("Fisioterapia", 45, 50.0)
        self._inserisci_visita_e_fattura(
            self.cf_mario, self.id_medico_luca, self.id_visita, "2024-05-10", 100.0, 1
        )
        self._inserisci_visita_e_fattura(
            self.cf_sara, self.id_medico_luca, self.id_fisioterapia, "2024-05-11", 50.0, 2
        )
        self._inserisci_visita_e_fattura(
            self.cf_mario, self.id_medico_sara, self.id_visita, "2024-06-01", 70.0, 3
        )
        with self.connessione() as conn:
            conn.execute(
                "INSERT INTO Appuntamento "
                "(data, oraInizio, stato, cf_paziente, id_medico, id_prestazione) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("2024-05-12", "12:00", "Programmato", self.cf_mario, self.id_medico_luca, self.id_visita),
            )

    def _inserisci_visita_e_fattura(self, cf, id_medico, id_prestazione, data, totale, progressivo):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Appuntamento "
                "(data, oraInizio, stato, cf_paziente, id_medico, id_prestazione) "
                "VALUES (?, '10:00', 'Completato', ?, ?, ?)",
                (data, cf, id_medico, id_prestazione),
            )
            id_appuntamento = cursor.lastrowid
            cursor = conn.execute(
                "INSERT INTO Pagamento (appuntamento_id, dataOraPagamento, importo, metodo) "
                "VALUES (?, ?, ?, 'Carta')",
                (id_appuntamento, f"{data} 10:30:00", totale),
            )
            id_pagamento = cursor.lastrowid
            conn.execute(
                "INSERT INTO Fattura "
                "(pagamento_id, cf_paziente, numeroFattura, dataOraEmissione, totale) "
                "VALUES (?, ?, ?, ?, ?)",
                (id_pagamento, cf, f"FATT-{progressivo:03d}", f"{data} 10:45:00", totale),
            )

    def test_genera_report_pazienti_aggrega_visite_e_pazienti_unici_per_periodo(self):
        report_mensile = self.reportistica.generaReportPazienti(2024, 5)
        report_annuale = self.reportistica.generaReportPazienti(2024)

        self.assertEqual(report_mensile.getDatiReport()["datiAggregati"], {
            "visite_completate": 2,
            "pazienti_unici": 2,
        })
        self.assertEqual(report_annuale.getDatiReport()["datiAggregati"]["visite_completate"], 3)
        self.assertEqual(report_mensile.getDatiReport()["meseRiferimento"], 5)

    def test_genera_report_fatturato_globale_e_ritorna_zero_senza_fatture(self):
        report_mese = self.reportistica.generaReportFatturatoGlobale(2024, 5)
        report_anno = self.reportistica.generaReportFatturatoGlobale(2024)
        report_vuoto = self.reportistica.generaReportFatturatoGlobale(2020)

        self.assertEqual(report_mese.getDatiReport()["datiAggregati"]["fatturato_globale"], 150.0)
        self.assertEqual(report_anno.getDatiReport()["datiAggregati"]["fatturato_globale"], 220.0)
        self.assertEqual(report_vuoto.getDatiReport()["datiAggregati"]["fatturato_globale"], 0.0)

    def test_genera_report_fatturato_per_prestazione(self):
        report = self.reportistica.generaReportFatturatoPrestazione(2024, 5)

        self.assertEqual(report.getDatiReport()["datiAggregati"], {
            "Visita": 100.0,
            "Fisioterapia": 50.0,
        })

    def test_genera_report_fatturato_per_medico(self):
        report_maggio = self.reportistica.generaReportFatturatoMedico(2024, 5)
        report_giugno = self.reportistica.generaReportFatturatoMedico(2024, 6)

        self.assertEqual(report_maggio.getDatiReport()["datiAggregati"], {
            "Dr. Verdi Luca": 150.0,
        })
        self.assertEqual(report_giugno.getDatiReport()["datiAggregati"], {
            "Dr. Neri Sofia": 70.0,
        })

    def test_genera_report_statistico_solo_per_visite_completate(self):
        report = self.reportistica.generaReportStatisticoPrestazioni(2024, 5)

        self.assertEqual(report.getDatiReport()["datiAggregati"], {
            "Visita": 1,
            "Fisioterapia": 1,
        })

    def test_genera_report_mensili_automatici_salva_tutte_le_categorie(self):
        with redirect_stdout(io.StringIO()):
            esito = self.reportistica.generaReportMensiliAutomatici(2024, 5)

        self.assertTrue(esito)
        report_salvati = self.righe(
            "SELECT tipoReport, annoRiferimento, meseRiferimento FROM Report "
            "WHERE annoRiferimento = 2024 AND meseRiferimento = 5"
        )
        self.assertEqual(len(report_salvati), 5)
        self.assertEqual({report["tipoReport"] for report in report_salvati}, {
            "Pazienti",
            "Fatturato Globale",
            "Fatturato Prestazione",
            "Fatturato Medico",
            "Statistico Prestazioni",
        })

    def test_get_lista_report_applica_filtri_anno_mese_e_tipo(self):
        self.reportistica.generaReportPazienti(2024, 5)
        self.reportistica.generaReportFatturatoGlobale(2024, 5)
        self.reportistica.generaReportPazienti(2024, 6)
        self.reportistica.generaReportPazienti(2023, 5)

        filtrati = self.reportistica.getListaReport(2024, 5, "Pazienti")
        mese = self.reportistica.getListaReport(2024, 5, "Tutti")
        tutti = self.reportistica.getListaReport(0, 0, "Tutti")
        self.assertEqual(len(filtrati), 1)
        self.assertEqual(filtrati[0]["tipoReport"], "Pazienti")
        self.assertEqual(len(mese), 2)
        self.assertEqual(len(tutti), 4)

    def test_visualizza_report_decodifica_json_e_gestisce_id_assente(self):
        report_creato = self.reportistica.generaReportPazienti(2024, 5)
        id_report = report_creato.getDatiReport()["id"]

        visualizzato = self.reportistica.visualizzaReport(id_report)
        self.assertEqual(visualizzato["id"], id_report)
        self.assertIsInstance(visualizzato["datiAggregati"], dict)
        self.assertEqual(visualizzato["datiAggregati"]["pazienti_unici"], 2)
        self.assertIsNone(self.reportistica.visualizzaReport(999))

    def test_esporta_report_restituisce_esito_e_mostra_contenuto(self):
        report = self.reportistica.generaReportPazienti(2024, 5)
        id_report = report.getDatiReport()["id"]

        self.assertFalse(self.reportistica.esportaReport(999, "PDF"))
        with redirect_stdout(io.StringIO()) as output:
            esportato = self.reportistica.esportaReport(id_report, "PDF")

        self.assertTrue(esportato)
        self.assertIn("Report_Pazienti_2024.pdf", output.getvalue())
        self.assertIn("visite_completate", output.getvalue())


if __name__ == "__main__":
    import unittest
    unittest.main()