import sqlite3
from datetime import date, datetime, time, timedelta
from contextlib import redirect_stdout
import io

from controllers.gestore_clinica import AccessoNegatoError
from controller_test_support import ControllerDatabaseTestCase


class TestGestoreClinica(ControllerDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.cf_paziente = self.inserisci_paziente()
        self.id_medico = self.inserisci_dipendente()
        self.id_prestazione = self.inserisci_prestazione()
        self.data_futura = date.today() + timedelta(days=2)

    def crea_appuntamento(self, **kwargs):
        valori = {
            "cf_paziente": self.cf_paziente,
            "id_medico": self.id_medico,
            "id_prestazione": self.id_prestazione,
            "data": self.data_futura.isoformat(),
            "ora": "10:00",
            "stato": "Programmato",
        }
        valori.update(kwargs)
        return self.inserisci_appuntamento(**valori)

    def test_get_prestazioni_disponibili_ricostruisce_i_modelli(self):
        prestazioni = self.clinica.getPrestazioniDisponibili()

        self.assertEqual(len(prestazioni), 1)
        self.assertEqual(prestazioni[0].getInfoPrestazione()["nomePrestazione"], "Visita")
        self.assertEqual(prestazioni[0].getCosto(), 50.0)

    def test_get_tutti_medici_e_pazienti_restituisce_dati_per_le_view(self):
        self.inserisci_dipendente("Sara", "Neri", "sara@example.com", "Password123", "Segretario")

        self.assertEqual(self.clinica.getTuttiMedici(), [
            {"id": self.id_medico, "nome": "Luca", "cognome": "Verdi"}
        ])
        self.assertEqual(self.clinica.getTuttiPazienti(), [
            {"cf": self.cf_paziente, "nome": "Mario", "cognome": "Rossi"}
        ])

    def test_aggiorna_anamnesi_crea_aggiorna_e_controlla_ruolo(self):
        self.assertTrue(self.clinica.aggiornaAnamnesi(self.cf_paziente, "Prima anamnesi"))
        self.assertTrue(self.clinica.aggiornaAnamnesi(self.cf_paziente, "Anamnesi aggiornata"))
        self.assertEqual(self.clinica.getCartellaClinica(self.cf_paziente)["anamnesiGenerica"], "Anamnesi aggiornata")
        with self.assertRaises(AccessoNegatoError):
            self.clinica.aggiornaAnamnesi(self.cf_paziente, "Non autorizzato", "Segretario")

    def test_get_cartella_clinica_assente_presente_e_ruolo_non_autorizzato(self):
        self.assertIsNone(self.clinica.getCartellaClinica(self.cf_paziente))
        self.clinica.aggiornaAnamnesi(self.cf_paziente, "Anamnesi")
        cartella = self.clinica.getCartellaClinica(self.cf_paziente)
        self.assertEqual(cartella["anamnesiGenerica"], "Anamnesi")
        self.assertIn("id", cartella)
        with self.assertRaises(AccessoNegatoError):
            self.clinica.getCartellaClinica(self.cf_paziente, "Amministratore")

    def test_crea_appuntamento_persistito_conflitto_medico_paziente_e_data_passata(self):
        creato, messaggio = self.clinica.creaAppuntamento(
            self.data_futura, time(10, 0), self.cf_paziente, self.id_medico, self.id_prestazione
        )
        self.assertTrue(creato, messaggio)

        conflitto_medico, messaggio_medico = self.clinica.creaAppuntamento(
            self.data_futura, time(10, 15), self.cf_paziente, self.id_medico, self.id_prestazione
        )
        self.assertFalse(conflitto_medico)
        self.assertIn("Conflitto Medico", messaggio_medico)

        altro_medico = self.inserisci_dipendente("Marco", "Bianchi", "marco@example.com", "Password123", "Medico")
        conflitto_paziente, messaggio_paziente = self.clinica.creaAppuntamento(
            self.data_futura, time(10, 15), self.cf_paziente, altro_medico, self.id_prestazione
        )
        self.assertFalse(conflitto_paziente)
        self.assertIn("Conflitto Paziente", messaggio_paziente)

        passato, messaggio_passato = self.clinica.creaAppuntamento(
            date.today() - timedelta(days=1), time(10, 0), self.cf_paziente, altro_medico, self.id_prestazione
        )
        self.assertFalse(passato)
        self.assertIn("passato", messaggio_passato)
        self.assertEqual(len(self.righe("SELECT * FROM Appuntamento")), 1)

    def test_annulla_appuntamento_cambia_stato_e_restituisce_esito(self):
        id_appuntamento = self.crea_appuntamento()

        self.assertTrue(self.clinica.annullaAppuntamento(id_appuntamento))
        self.assertFalse(self.clinica.annullaAppuntamento(999))
        self.assertEqual(self.righe("SELECT stato FROM Appuntamento")[0]["stato"], "Annullato")

    def test_get_dettagli_appuntamento_trovato_e_assente(self):
        id_appuntamento = self.crea_appuntamento()

        dettagli = self.clinica.getDettagliAppuntamento(id_appuntamento)
        self.assertEqual(dettagli["id"], id_appuntamento)
        self.assertEqual(dettagli["nome"], "Mario")
        self.assertEqual(dettagli["cognome"], "Rossi")
        self.assertEqual(self.clinica.getDettagliAppuntamento(999), {})

    def test_modifica_orario_salva_e_cancella_memo_collegato(self):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Memo (dataInvioProgrammata, inviato) VALUES (?, 1)",
                (self.data_futura.isoformat(),),
            )
            id_memo = cursor.lastrowid
            cursor.execute(
                "INSERT INTO Appuntamento "
                "(data, oraInizio, stato, cf_paziente, id_medico, id_prestazione, id_memo) "
                "VALUES (?, ?, 'Programmato', ?, ?, ?, ?)",
                (self.data_futura.isoformat(), "10:00", self.cf_paziente, self.id_medico, self.id_prestazione, id_memo),
            )
            id_appuntamento = cursor.lastrowid

        nuova_data = self.data_futura + timedelta(days=1)
        risultato, messaggio = self.clinica.modificaOrarioAppuntamento(
            id_appuntamento, nuova_data, time(11, 30)
        )
        self.assertTrue(risultato, messaggio)
        self.assertEqual(self.righe("SELECT data, oraInizio, id_memo FROM Appuntamento")[0], {
            "data": nuova_data.isoformat(), "oraInizio": "11:30", "id_memo": None
        })
        self.assertEqual(self.righe("SELECT * FROM Memo"), [])

    def test_modifica_orario_rifiuta_appuntamento_assente_o_concluso(self):
        self.assertFalse(self.clinica.modificaOrarioAppuntamento(999, self.data_futura, time(12, 0))[0])
        self.crea_appuntamento(stato="Completato")
        risultato, messaggio = self.clinica.modificaOrarioAppuntamento(
            1, self.data_futura + timedelta(days=1), time(12, 0)
        )
        self.assertFalse(risultato)
        self.assertIn("impossibile modificare", messaggio)

    def test_get_agenda_medico_ordina_e_filtra_per_medico_e_data(self):
        self.crea_appuntamento(ora="11:00")
        self.crea_appuntamento(ora="09:00", cf_paziente="RSSMRA80A01H501Z")
        altro_medico = self.inserisci_dipendente("Marco", "Bianchi", "marco@example.com", "Password123", "Medico")
        self.crea_appuntamento(ora="08:00", id_medico=altro_medico)

        agenda = self.clinica.getAgendaMedico(self.id_medico, self.data_futura)
        self.assertEqual([riga["oraInizio"] for riga in agenda], ["09:00", "11:00"])
        self.assertEqual(self.clinica.getAgendaMedico(self.id_medico, self.data_futura + timedelta(days=1)), [])

    def test_aggiungi_prestazione_inserisce_e_rifiuta_nome_duplicato_senza_distinguere_case(self):
        inserita, _ = self.clinica.aggiungiPrestazione("Fisioterapia", 45, 75.0)
        duplicata, messaggio = self.clinica.aggiungiPrestazione("fIsIoTeRaPiA", 30, 50.0)

        self.assertTrue(inserita)
        self.assertFalse(duplicata)
        self.assertIn("Esiste già", messaggio)
        prestazioni = self.clinica.getPrestazioniDisponibili()
        nuova_prestazione = next(
            prestazione for prestazione in prestazioni
            if prestazione.getInfoPrestazione()["nomePrestazione"] == "Fisioterapia"
        )
        self.assertEqual(nuova_prestazione.getCosto(), 75.0)

    def test_registra_valutazione_completa_appuntamento_e_verifica_permessi(self):
        id_appuntamento = self.crea_appuntamento()

        self.assertTrue(self.clinica.registraValutazioneFunzionale(
            id_appuntamento, "Nessuna", "Riposo", "Basso", 8, self.id_medico
        ))
        riga = self.righe("SELECT stato, id_valutazione FROM Appuntamento")[0]
        self.assertEqual(riga["stato"], "Completato")
        self.assertIsNotNone(riga["id_valutazione"])
        self.assertFalse(self.clinica.registraValutazioneFunzionale(
            999, "Nessuna", "", "Basso", 8, self.id_medico
        ))

        id_segretario = self.inserisci_dipendente(
            "Sara", "Neri", "sara@example.com", "Password123", "Segretario"
        )
        with self.assertRaises(AccessoNegatoError):
            self.clinica.registraValutazioneFunzionale(
                id_appuntamento, "x", "x", "x", 5, id_segretario
            )

    def test_invia_promemoria_crea_memo_e_non_lo_invia_due_volte(self):
        id_appuntamento = self.crea_appuntamento(data=(date.today() + timedelta(days=1)).isoformat())

        with redirect_stdout(io.StringIO()):
            primo_invio = self.clinica.inviaPromemoriaAutomatici()
            secondo_invio = self.clinica.inviaPromemoriaAutomatici()

        self.assertEqual(primo_invio, 1)
        self.assertEqual(secondo_invio, 0)
        memo = self.righe("SELECT dataInvioProgrammata, inviato FROM Memo")
        self.assertEqual(memo, [{"dataInvioProgrammata": (date.today() + timedelta(days=1)).isoformat(), "inviato": 1}])
        self.assertIsNotNone(self.righe("SELECT id_memo FROM Appuntamento WHERE id = ?", (id_appuntamento,))[0]["id_memo"])

    def test_storico_paziente_include_medico_stato_e_referto(self):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO ValutazioneFunzionale (anomalie, noteAggiuntive, prevOvertraining, valutazioneClinica) "
                "VALUES ('Nessuna', 'Riposo', 'Basso', 8)"
            )
            id_valutazione = cursor.lastrowid
        self.crea_appuntamento(stato="Completato", id_valutazione=id_valutazione)

        storico = self.clinica.getStoricoPaziente(self.cf_paziente)
        self.assertEqual(len(storico), 1)
        self.assertEqual(storico[0]["nome_medico"], "Luca")
        self.assertEqual(storico[0]["nomePrestazione"], "Visita")
        self.assertEqual(storico[0]["id_valutazione"], id_valutazione)

    def test_get_dettagli_valutazione_trovata_assente_e_permessi(self):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO ValutazioneFunzionale (anomalie, noteAggiuntive, prevOvertraining, valutazioneClinica) "
                "VALUES ('Nessuna', 'Riposo', 'Basso', 8)"
            )
            id_valutazione = cursor.lastrowid

        dettagli = self.clinica.getDettagliValutazione(id_valutazione)
        self.assertEqual(dettagli["valutazioneClinica"], 8)
        self.assertEqual(self.clinica.getDettagliValutazione(999), {})
        self.assertEqual(self.clinica.getDettagliValutazione(0), {})
        with self.assertRaises(AccessoNegatoError):
            self.clinica.getDettagliValutazione(id_valutazione, "Segretario")


if __name__ == "__main__":
    import unittest
    unittest.main()