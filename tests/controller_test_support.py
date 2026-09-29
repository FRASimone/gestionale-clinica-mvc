import io
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from controllers.gestore_amministrativa import GestoreAmministrativa
from controllers.gestore_anagrafica import GestoreAnagrafica
from controllers.gestore_clinica import GestoreClinica
from controllers.gestore_reportistica import GestoreReportistica
from database import db_manager


class ControllerDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.directory_temporanea = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.directory_temporanea.name) / "clinica_test.db")

        with patch.object(db_manager, "DB_PATH", self.db_path):
            with redirect_stdout(io.StringIO()):
                db_manager.inizializza_database()

        self.anagrafica = GestoreAnagrafica(self.db_path)
        self.clinica = GestoreClinica(self.db_path)
        self.amministrativa = GestoreAmministrativa(self.db_path)
        self.reportistica = GestoreReportistica(self.db_path)

    def tearDown(self):
        self.directory_temporanea.cleanup()

    @contextmanager
    def connessione(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def inserisci_dipendente(
        self,
        nome="Luca",
        cognome="Verdi",
        email="luca@example.com",
        password="Password123",
        ruolo="Medico",
    ):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Dipendente (nome, cognome, email, password, ruolo) "
                "VALUES (?, ?, ?, ?, ?)",
                (nome, cognome, email, password, ruolo),
            )
            return cursor.lastrowid

    def inserisci_paziente(
        self,
        cf="RSSMRA80A01H501Z",
        nome="Mario",
        cognome="Rossi",
        email="mario@example.com",
        telefono="3331234567",
        is_agonista=False,
    ):
        with self.connessione() as conn:
            conn.execute(
                "INSERT INTO Paziente (cf, nome, cognome, email, telefono, isAgonista) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (cf, nome, cognome, email, telefono, int(is_agonista)),
            )
        return cf

    def inserisci_prestazione(self, nome="Visita", durata=30, costo=50.0):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Prestazione (nomePrestazione, durataMinuti, costoBase) "
                "VALUES (?, ?, ?)",
                (nome, durata, costo),
            )
            return cursor.lastrowid

    def inserisci_appuntamento(
        self,
        cf_paziente="RSSMRA80A01H501Z",
        id_medico=1,
        id_prestazione=1,
        data="2025-05-15",
        ora="10:00",
        stato="Completato",
        id_memo=None,
        id_valutazione=None,
    ):
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Appuntamento "
                "(data, oraInizio, stato, cf_paziente, id_medico, id_prestazione, id_memo, id_valutazione) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (data, ora, stato, cf_paziente, id_medico, id_prestazione, id_memo, id_valutazione),
            )
            return cursor.lastrowid

    def righe(self, query, parametri=()):
        with self.connessione() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(riga) for riga in conn.execute(query, parametri).fetchall()]


class TestGestoreAnagrafica(ControllerDatabaseTestCase):
    def test_registra_dipendente_salva_e_rifiuta_duplicati_e_password_non_valide(self):
        with redirect_stdout(io.StringIO()):
            registrato, messaggio = self.anagrafica.registraDipendente(
                "Anna", "Neri", "anna@example.com", "Password123", "Segretario"
            )
            duplicato, messaggio_duplicato = self.anagrafica.registraDipendente(
                "Anna", "Neri", "anna@example.com", "Password123", "Segretario"
            )

        self.assertTrue(registrato)
        self.assertIn("Registrazione completata", messaggio)
        self.assertFalse(duplicato)
        self.assertIn("email", messaggio_duplicato)
        self.assertFalse(self.anagrafica.registraDipendente("A", "B", "x", "short", "Medico")[0])
        self.assertFalse(self.anagrafica.registraDipendente("A", "B", "x", "passwordonly", "Medico")[0])
        self.assertEqual(self.anagrafica.getDipendenteByEmail("anna@example.com"), 1)

    def test_modifica_ruolo_aggiorna_e_rimuove_specializzazioni_mediche(self):
        id_medico = self.inserisci_dipendente()
        with self.connessione() as conn:
            conn.execute("INSERT INTO Specializzazione (nome, dettagli) VALUES (?, ?)", ("Cardiologia", "Cuore"))
            id_specializzazione = conn.execute("SELECT id FROM Specializzazione").fetchone()[0]
            conn.execute(
                "INSERT INTO Medico_Specializzazione (id_medico, id_specializzazione) VALUES (?, ?)",
                (id_medico, id_specializzazione),
            )

        self.assertTrue(self.anagrafica.modifica_ruolo(id_medico, "Segretario"))
        self.assertFalse(self.anagrafica.modifica_ruolo(999, "Medico"))
        self.assertEqual(self.righe("SELECT ruolo FROM Dipendente WHERE id = ?", (id_medico,))[0]["ruolo"], "Segretario")
        self.assertEqual(self.righe("SELECT * FROM Medico_Specializzazione"), [])

    def test_get_tutti_dipendenti_restituisce_dati_senza_password(self):
        self.inserisci_dipendente()

        dipendenti = self.anagrafica.get_tutti_dipendenti()

        self.assertEqual(len(dipendenti), 1)
        self.assertEqual(dipendenti[0]["email"], "luca@example.com")
        self.assertNotIn("password", dipendenti[0])

    def test_assegna_specializzazione_e_rifiuta_doppioni(self):
        id_medico = self.inserisci_dipendente()
        with self.connessione() as conn:
            cursor = conn.execute(
                "INSERT INTO Specializzazione (nome, dettagli) VALUES (?, ?)",
                ("Neurologia", "Sistema nervoso"),
            )
            id_specializzazione = cursor.lastrowid

        with redirect_stdout(io.StringIO()):
            self.assertTrue(self.anagrafica.assegnaSpecializzazione(id_medico, id_specializzazione))
            self.assertFalse(self.anagrafica.assegnaSpecializzazione(id_medico, id_specializzazione))
        self.assertEqual(len(self.righe("SELECT * FROM Medico_Specializzazione")), 1)

    def test_cerca_utente_per_email_trovato_e_assente(self):
        self.inserisci_dipendente()

        self.assertEqual(self.anagrafica.cercaUtentePerEmail("luca@example.com")["nome"], "Luca")
        self.assertIsNone(self.anagrafica.cercaUtentePerEmail("assente@example.com"))

    def test_login_restituisce_il_modello_del_ruolo_e_gestisce_errori(self):
        id_medico = self.inserisci_dipendente()
        self.inserisci_dipendente(
            "Sara", "Neri", "sara@example.com", "Password123", "Segretario"
        )
        self.inserisci_dipendente(
            "Paolo", "Blu", "paolo@example.com", "Password123", "Amministratore"
        )

        medico, stato_medico = self.anagrafica.login("luca@example.com", "Password123", "Medico")
        segretario, stato_segretario = self.anagrafica.login("sara@example.com", "Password123", "Segretario")
        admin, stato_admin = self.anagrafica.login("paolo@example.com", "Password123", "Amministratore")
        self.assertEqual((stato_medico, stato_segretario, stato_admin), ("ok", "ok", "ok"))
        self.assertEqual(medico.getId(), id_medico)
        self.assertEqual(medico.getRuolo(), "Medico")
        self.assertEqual(segretario.getRuolo(), "Segretario")
        self.assertEqual(admin.getRuolo(), "Amministratore")
        self.assertEqual(self.anagrafica.login("luca@example.com", "errata", "Medico")[1], "credenziali_errate")
        self.assertEqual(self.anagrafica.login("assente@example.com", "x", "Medico")[1], "utente_inesistente")

    def test_recupera_credenziali_con_e_senza_account(self):
        self.inserisci_dipendente()
        with redirect_stdout(io.StringIO()) as output:
            esito, messaggio = self.anagrafica.recuperaCredenziali("luca@example.com")

        self.assertTrue(esito)
        self.assertIn("inviato", messaggio)
        self.assertIn("Password123", output.getvalue())
        self.assertFalse(self.anagrafica.recuperaCredenziali("assente@example.com")[0])

    def test_aggiungi_paziente_salva_e_rifiuta_codice_fiscale_duplicato(self):
        paziente = self.anagrafica.aggiungiPaziente(
            "RSSMRA80A01H501Z", "Mario", "Rossi", "mario@example.com", "3331234567", True
        )

        self.assertEqual(paziente.getDatiPaziente()["cf"], "RSSMRA80A01H501Z")
        self.assertIsNone(self.anagrafica.aggiungiPaziente(
            "RSSMRA80A01H501Z", "Mario", "Rossi", "mario@example.com", "3331234567", True
        ))
        self.assertEqual(self.righe("SELECT isAgonista FROM Paziente")[0]["isAgonista"], 1)

    def test_ricerca_paziente_per_codice_fiscale_o_cognome(self):
        self.inserisci_paziente()

        per_cf = self.anagrafica.ricercaPaziente("RSSMRA80A01H501Z")
        per_cognome = self.anagrafica.ricercaPaziente("Ross")
        self.assertEqual(len(per_cf), 1)
        self.assertEqual(len(per_cognome), 1)
        self.assertEqual(per_cf[0].getDatiPaziente(), per_cognome[0].getDatiPaziente())
        self.assertEqual(self.anagrafica.ricercaPaziente("inesistente"), [])

    def test_modifica_scheda_paziente_salva_dati_e_rifiuta_dati_incompleti(self):
        self.inserisci_paziente()
        nuovi_dati = {"email": "nuova@example.com", "telefono": "3337654321", "isAgonista": True}

        self.assertTrue(self.anagrafica.modificaSchedaPaziente("RSSMRA80A01H501Z", nuovi_dati))
        self.assertFalse(self.anagrafica.modificaSchedaPaziente("RSSMRA80A01H501Z", {"email": "x"}))
        self.assertFalse(self.anagrafica.modificaSchedaPaziente("CF-ASSENTE", nuovi_dati))
        riga = self.righe("SELECT email, telefono, isAgonista FROM Paziente")[0]
        self.assertEqual(riga, {"email": "nuova@example.com", "telefono": "3337654321", "isAgonista": 1})

    def test_get_tutte_specializzazioni_e_get_dipendente_by_email(self):
        id_medico = self.inserisci_dipendente()
        with self.connessione() as conn:
            conn.execute("INSERT INTO Specializzazione (nome, dettagli) VALUES (?, ?)", ("Ortopedia", "Ossa"))

        self.assertEqual(self.anagrafica.getTutteSpecializzazioni(), [
            {"id": 1, "nome": "Ortopedia"}
        ])
        self.assertEqual(self.anagrafica.getDipendenteByEmail("luca@example.com"), id_medico)
        self.assertEqual(self.anagrafica.getDipendenteByEmail("assente@example.com"), -1)


if __name__ == "__main__":
    unittest.main()