import io
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, time, timedelta
from pathlib import Path
from unittest.mock import patch

from controllers.gestore_anagrafica import GestoreAnagrafica
from controllers.gestore_clinica import GestoreClinica
from database import db_manager
from models.dipendente import Medico
from models.paziente import Paziente
from models.prestazione import Prestazione


class TestScambioModelliControllerDatabase(unittest.TestCase):
    def setUp(self):
        self.directory_temporanea = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.directory_temporanea.name) / "clinica_test.db")

        with patch.object(db_manager, "DB_PATH", self.db_path):
            with redirect_stdout(io.StringIO()):
                db_manager.inizializza_database()

        self.gestore_anagrafica = GestoreAnagrafica(self.db_path)
        self.gestore_clinica = GestoreClinica(self.db_path)

    def tearDown(self):
        self.directory_temporanea.cleanup()

    def _crea_paziente(self):
        paziente = self.gestore_anagrafica.aggiungiPaziente(
            "RSSMRA80A01H501Z",
            "Mario",
            "Rossi",
            "mario@example.com",
            "3331234567",
            False,
        )
        self.assertIsInstance(paziente, Paziente)
        return paziente

    def _crea_medico(self):
        with redirect_stdout(io.StringIO()):
            registrato, _ = self.gestore_anagrafica.registraDipendente(
                "Luigi",
                "Verdi",
                "luigi@example.com",
                "Password123",
                "Medico",
            )

        self.assertTrue(registrato)
        medico, stato = self.gestore_anagrafica.login(
            "luigi@example.com", "Password123", "Medico"
        )
        self.assertEqual(stato, "ok")
        self.assertIsInstance(medico, Medico)
        return medico

    def test_paziente_salvato_e_ricostruito_dal_controller(self):
        paziente_salvato = self._crea_paziente()

        risultati = self.gestore_anagrafica.ricercaPaziente(
            paziente_salvato.getCf()
        )

        self.assertEqual(len(risultati), 1)
        paziente_letto = risultati[0]
        self.assertIsInstance(paziente_letto, Paziente)
        self.assertEqual(paziente_letto.getDatiPaziente(), {
            "cf": "RSSMRA80A01H501Z",
            "nome": "Mario",
            "cognome": "Rossi",
            "email": "mario@example.com",
            "telefono": "3331234567",
            "isAgonista": False,
        })

    def test_modifica_paziente_persistita_e_visibile_sul_model_ricaricato(self):
        paziente = self._crea_paziente()

        aggiornato = self.gestore_anagrafica.modificaSchedaPaziente(
            paziente.getCf(),
            {
                "email": "nuovo@example.com",
                "telefono": "3337654321",
                "isAgonista": True,
            },
        )
        risultati = self.gestore_anagrafica.ricercaPaziente(paziente.getCf())

        self.assertTrue(aggiornato)
        self.assertEqual(len(risultati), 1)
        self.assertEqual(risultati[0].getDatiPaziente()["email"], "nuovo@example.com")
        self.assertEqual(risultati[0].getDatiPaziente()["telefono"], "3337654321")
        self.assertTrue(risultati[0].getDatiPaziente()["isAgonista"])

    def test_modelli_passati_al_controller_salvati_nell_appuntamento(self):
        paziente = self._crea_paziente()
        medico = self._crea_medico()

        inserita, _ = self.gestore_clinica.aggiungiPrestazione(
            "Visita di prova", 30, 60.0
        )
        self.assertTrue(inserita)
        prestazioni = self.gestore_clinica.getPrestazioniDisponibili()
        self.assertEqual(len(prestazioni), 1)
        prestazione = prestazioni[0]
        self.assertIsInstance(prestazione, Prestazione)

        data_appuntamento = date.today() + timedelta(days=1)
        creato, messaggio = self.gestore_clinica.creaAppuntamento(
            data_appuntamento,
            time(10, 0),
            paziente.getCf(),
            medico.getId(),
            prestazione.getInfoPrestazione()["id"],
        )

        self.assertTrue(creato, messaggio)
        agenda = self.gestore_clinica.getAgendaMedico(
            medico.getId(), data_appuntamento
        )
        self.assertEqual(len(agenda), 1)
        self.assertEqual(agenda[0]["cf_paziente"], paziente.getCf())
        self.assertEqual(agenda[0]["nome_paziente"], "Mario")
        self.assertEqual(agenda[0]["nomePrestazione"], "Visita di prova")

        with sqlite3.connect(self.db_path) as conn:
            riga = conn.execute(
                "SELECT stato, cf_paziente, id_medico, id_prestazione "
                "FROM Appuntamento"
            ).fetchone()

        self.assertEqual(
            riga,
            ("Programmato", paziente.getCf(), medico.getId(), prestazione.getInfoPrestazione()["id"]),
        )


if __name__ == "__main__":
    unittest.main()