import io
import json
import sqlite3
import unittest
from contextlib import contextmanager
from profile_data import schema, read
from profile_edit import handle


class ProfileEditTest(unittest.TestCase):
    def test_user_isolation_history_and_validation(self):
        db = sqlite3.connect(':memory:')
        schema(db)

        @contextmanager
        def connection():
            yield db

        class Handler:
            def reply(self, data, status=200):
                return status, data

        def save(profile, weight):
            handler = Handler()
            body = json.dumps({'profile': profile, 'profileData': {
                'heightCm': 175, 'weightKg': weight, 'weightDate': '2026-01-01'}}).encode()
            handler.headers = {'Content-Length': str(len(body))}
            handler.rfile = io.BytesIO(body)
            return handle(handler, connection)

        self.assertEqual(save('1', 80)[0], 200)
        self.assertEqual(save('2', 65)[0], 200)
        self.assertEqual(save('1', 79)[0], 200)
        self.assertEqual(read(db, '1')['weightKg'], 79)
        self.assertEqual(len(read(db, '1')['weightHistory']), 2)
        self.assertEqual(read(db, '2')['weightKg'], 65)
        self.assertEqual(save('1', 900)[0], 400)
        self.assertEqual(read(db, '1')['weightKg'], 79)
        self.assertEqual(save('5', 80)[0], 400)
        db.close()
