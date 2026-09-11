import unittest
from datetime import datetime
from models.memo import Memo

class TestMemo(unittest.TestCase):
    def setUp(self):
        self.data_invio = datetime(2023, 11, 19, 9, 0)
        self.memo = Memo(1, self.data_invio)

    def test_getters(self):
        self.assertEqual(self.memo.getId(), 1)
        self.assertEqual(self.memo.getDataInvioProgrammata(), self.data_invio)
        self.assertFalse(self.memo.isInviato())

    def test_segna_come_inviato(self):
        self.memo.segnaComeInviato()
        self.assertTrue(self.memo.isInviato())

if __name__ == '__main__':
    unittest.main()
