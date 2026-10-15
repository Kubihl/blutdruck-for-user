import contextlib
import importlib.util
import io
import json
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / 'app'
spec = importlib.util.spec_from_file_location('measurement_import', ROOT / 'measurement_import.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Handler:
    def __init__(self, body):
        data = json.dumps(body).encode()
        self.headers = {'Content-Length': str(len(data)), 'Content-Type': 'application/json'}
        self.rfile = io.BytesIO(data)
        self.result = None

    def reply(self, data, status=200):
        self.result = (status, data)


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.dbpath = Path(self.temp.name) / 'test.sqlite'
        with self.connection() as db:
            db.execute('CREATE TABLE readings(id TEXT PRIMARY KEY,systolic INTEGER,diastolic INTEGER,pulse INTEGER,measuredAt TEXT,note TEXT,origin TEXT,profile TEXT,profileName TEXT)')
            db.execute('CREATE TABLE profile_names(profile TEXT PRIMARY KEY,name TEXT NOT NULL)')
            db.execute('CREATE TABLE ui_state(id TEXT PRIMARY KEY,hidden INTEGER NOT NULL DEFAULT 0,note TEXT)')
        self.item_id = str(uuid.uuid4())
        self.package = {'format': 'puls180-pc-transfer', 'version': 1, 'profileName': 'Anna', 'readings': [
            {'id': self.item_id, 'systolic': 125, 'diastolic': 82, 'pulse': 71,
             'measuredAt': '2026-09-25T10:00:00Z', 'note': 'Test'}]}

    def tearDown(self):
        self.temp.cleanup()

    @contextlib.contextmanager
    def connection(self):
        db = sqlite3.connect(self.dbpath)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def call(self, profile, commit, restore=False):
        handler = Handler({'package': self.package, 'profile': profile, 'commit': commit, 'restoreHidden': restore})
        module.handle(handler, self.connection)
        return handler.result

    def test_preview_import_deduplicate_and_cross_profile_guard(self):
        with self.connection() as db:
            db.execute('INSERT INTO profile_names(profile,name) VALUES(?,?)', ('2', 'Anna'))
        self.assertEqual(self.call('2', False)[1]['new'], 1)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM readings').fetchone()[0], 0)
        self.assertEqual(self.call('2', True)[1]['added'], 1)
        self.assertEqual(self.call('2', True)[1]['added'], 0)
        self.assertEqual(self.call('1', True)[0], 400)
        with self.connection() as db:
            self.assertEqual(tuple(db.execute('SELECT profile,profileName FROM readings').fetchone()), ('2', 'Anna'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM readings').fetchone()[0], 1)

    def test_unlabelled_profile_is_rejected(self):
        self.assertEqual(self.call('2', False)[0], 400)
        self.assertEqual(self.call('2', True)[0], 400)

    def test_invalid_file_does_not_write(self):
        self.package['readings'][0]['systolic'] = 60
        self.assertEqual(self.call('1', True)[0], 400)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM readings').fetchone()[0], 0)

    def test_different_person_cannot_enter_occupied_profile(self):
        with self.connection() as db:
            db.execute('INSERT INTO profile_names(profile,name) VALUES(?,?)', ('2', 'Berta'))
        self.assertEqual(self.call('2', False)[0], 400)
        self.assertEqual(self.call('2', True)[0], 400)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM readings').fetchone()[0], 0)


    def test_third_and_fourth_users_stay_separate(self):
        with self.connection() as db:
            db.executemany('INSERT INTO profile_names(profile,name) VALUES(?,?)',
                           [('3', 'Anna'), ('4', 'Betty')])
        self.assertEqual(self.call('3', True)[1]['added'], 1)
        self.assertEqual(self.call('4', True)[0], 400)
        self.package['profileName'] = 'Betty'
        self.package['readings'][0]['id'] = str(uuid.uuid4())
        self.assertEqual(self.call('4', True)[1]['added'], 1)
        with self.connection() as db:
            self.assertEqual([tuple(row) for row in db.execute(
                'SELECT profile,profileName FROM readings ORDER BY profile')],
                [('3', 'Anna'), ('4', 'Betty')])

    def test_hidden_duplicate_needs_explicit_restore(self):
        with self.connection() as db:
            db.execute('INSERT INTO profile_names(profile,name) VALUES(?,?)', ('1', 'Anna'))
        self.assertEqual(self.call('1', True)[1]['added'], 1)
        with self.connection() as db:
            db.execute('INSERT INTO ui_state(id,hidden,note) VALUES(?,?,?)', (self.item_id, 1, 'PC-Notiz'))
        preview = self.call('1', False)[1]
        self.assertEqual((preview['new'], preview['hiddenDuplicates']), (0, 1))
        self.assertEqual(self.call('1', True)[1]['restored'], 0)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT hidden FROM ui_state WHERE id=?', (self.item_id,)).fetchone()[0], 1)
        self.assertEqual(self.call('1', True, restore=True)[1]['restored'], 1)
        with self.connection() as db:
            self.assertEqual(tuple(db.execute('SELECT hidden,note FROM ui_state WHERE id=?', (self.item_id,)).fetchone()), (0, 'PC-Notiz'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM readings').fetchone()[0], 1)

if __name__ == '__main__':
    unittest.main()



