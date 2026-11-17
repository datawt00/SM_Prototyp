"""Tests der Geschaeftslogik; brauchen keine externen Python-Pakete."""
import importlib.util
import os
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BookingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        os.environ['PARKSMART_DB'] = str(Path(cls.tmp.name) / 'demo.sqlite3')
        os.environ['PARKSMART_LED_MODE'] = 'simulation'
        spec = importlib.util.spec_from_file_location('parksmart_server', ROOT / 'server.py')
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.mod.initialize_db()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.mod.reset_demo()
        self.day = (date.today() + timedelta(days=1)).isoformat()

    def test_booking_and_cancel(self):
        m = self.mod
        m.create_booking({'date': self.day, 'spot': 'P2', 'owner': 'PT01'})
        self.assertIn('P2', m.booked_ids(self.day))
        m.cancel_booking({'date': self.day, 'spot': 'P2', 'owner': 'PT01'})
        self.assertNotIn('P2', m.booked_ids(self.day))

    def test_no_double_booking(self):
        m = self.mod
        m.create_booking({'date': self.day, 'spot': 'P2', 'owner': 'PT01'})
        with self.assertRaises(ValueError):
            m.create_booking({'date': self.day, 'spot': 'P2', 'owner': 'AN02'})

    def test_one_booking_per_user_and_day(self):
        m = self.mod
        m.create_booking({'date': self.day, 'spot': 'P1', 'owner': 'PT01'})
        with self.assertRaises(ValueError):
            m.create_booking({'date': self.day, 'spot': 'P3', 'owner': 'pt01'})

    def test_wrong_owner_cannot_cancel(self):
        m = self.mod
        m.create_booking({'date': self.day, 'spot': 'P4', 'owner': 'PT01'})
        with self.assertRaises(ValueError):
            m.cancel_booking({'date': self.day, 'spot': 'P4', 'owner': 'ZZ99'})
        self.assertIn('P4', m.booked_ids(self.day))

    def test_preview_date(self):
        m = self.mod
        m.set_preview({'date': self.day})
        self.assertEqual(m.led_day(), self.day)
        m.set_preview({'date': ''})
        self.assertEqual(m.led_day(), date.today().isoformat())

    def test_past_date_rejected(self):
        with self.assertRaises(ValueError):
            self.mod.valid_day((date.today()-timedelta(days=1)).isoformat())


if __name__ == '__main__':
    unittest.main()
