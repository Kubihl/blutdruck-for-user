import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
import unittest
import test_measurement_import as base
from profile_data import read


class ProfileTransferTest(unittest.TestCase):
    connection = base.ImportTest.connection
    call = base.ImportTest.call
    tearDown = base.ImportTest.tearDown
    def setUp(self):
        base.ImportTest.setUp(self)
        with self.connection() as db:
            db.execute("INSERT INTO profile_names VALUES('2','Anna')")
        self.package['profileData'] = {'heightCm': 178, 'weightKg': 84,
                                      'weightDate': '2026-10-01', 'weightHistory': []}

    def test_preview_is_read_only_and_confirm_is_per_user(self):
        self.assertEqual(self.call('2', False)[0], 200)
        with self.connection() as db:
            self.assertIsNone(read(db, '2'))
        self.assertEqual(self.call('2', True)[0], 200)
        with self.connection() as db:
            self.assertEqual(read(db, '2')['weightKg'], 84)
            self.assertIsNone(read(db, '1'))

    def test_repeat_and_older_import_preserve_newer_weight(self):
        self.call('2', True)
        self.call('2', True)
        with self.connection() as db:
            self.assertEqual(len(read(db, '2')['weightHistory']), 1)
        self.package['profileData'].update(weightKg=85, weightDate='2026-09-01')
        self.assertEqual(self.call('2', True)[0], 200)
        with self.connection() as db:
            self.assertEqual(read(db, '2')['weightKg'], 84)
            self.assertEqual(len(read(db, '2')['weightHistory']), 2)

    def test_bad_profile_rolls_back_measurements(self):
        self.package['profileData']['weightKg'] = float('nan')
        self.assertEqual(self.call('2', True)[0], 400)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM readings').fetchone()[0], 0)

    def test_legacy_package_does_not_remove_profile(self):
        self.call('2', True)
        del self.package['profileData']
        self.assertEqual(self.call('2', True)[0], 200)
        with self.connection() as db:
            self.assertEqual(read(db, '2')['heightCm'], 178)

    def test_wrong_person_cannot_import_profile(self):
        self.assertEqual(self.call('1', True)[0], 400)
        with self.connection() as db:
            self.assertIsNone(read(db, '1'))
