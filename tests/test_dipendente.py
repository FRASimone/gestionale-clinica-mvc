import unittest
from models.dipendente import Dipendente, Medico, Segretario, Amministratore

class TestDipendente(unittest.TestCase):
    def setUp(self):
        self.dipendente = Dipendente(1, "Mario", "Rossi", "mario.rossi@email.com", "password123", "Generico")
        self.medico = Medico(2, "Luigi", "Verdi", "luigi.verdi@email.com", "medico123")
        self.segretario = Segretario(3, "Anna", "Neri", "anna.neri@email.com", "segretario123")
        self.admin = Amministratore(4, "Paolo", "Gialli", "paolo.gialli@email.com", "admin123")

    def test_dipendente_getters(self):
        self.assertEqual(self.dipendente.getId(), 1)
        self.assertEqual(self.dipendente.getNome(), "Mario")
        self.assertEqual(self.dipendente.getCognome(), "Rossi")
        self.assertEqual(self.dipendente.getEmail(), "mario.rossi@email.com")
        self.assertEqual(self.dipendente.getRuolo(), "Generico")
        self.assertEqual(self.dipendente.getInfo(), "Mario Rossi (Generico)")

    def test_set_password(self):
        # Noi possiamo testare setPassword chiamandolo (non abbiamo un getPassword,
        # ma se ci fosse verificheremmo quello. In assenza, testiamo che non dia errori).
        try:
            self.dipendente.setPassword("nuova_password")
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

    def test_medico_ruolo(self):
        self.assertEqual(self.medico.getRuolo(), "Medico")
        self.assertEqual(self.medico.getInfo(), "Luigi Verdi (Medico)")

    def test_medico_specializzazioni_appuntamenti(self):
        self.assertEqual(len(self.medico.getSpecializzazioni()), 0)
        self.assertEqual(len(self.medico.getAppuntamenti()), 0)
        
        self.medico.setSpecializzazioni(["Cardiologia", "Neurologia"])
        self.assertEqual(self.medico.getSpecializzazioni(), ["Cardiologia", "Neurologia"])
        
        self.medico.aggiungiAppuntamento("Appuntamento1")
        self.assertEqual(self.medico.getAppuntamenti(), ["Appuntamento1"])

    def test_segretario_ruolo(self):
        self.assertEqual(self.segretario.getRuolo(), "Segretario")

    def test_admin_ruolo(self):
        self.assertEqual(self.admin.getRuolo(), "Amministratore")

if __name__ == '__main__':
    unittest.main()
