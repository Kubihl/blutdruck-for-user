import unittest
from unittest.mock import patch
from server import Handler


class ServerIdentityTest(unittest.TestCase):
    def request(self, path):
        handler = object.__new__(Handler)
        handler.path = path
        handler.headers = {'Host': '127.0.0.1:18775'}
        handler.reply = lambda data, status=200, **kw: (status, data)
        return handler.do_GET()

    def test_launcher_identifies_locked_diary(self):
        with patch('pc_lock.allowed', return_value=False):
            self.assertEqual(self.request('/api/identity'), (200, {
                'app': 'blutdruck-sales-desktop', 'version': '5.12'}))

    def test_profile_remains_protected_when_locked(self):
        with patch('pc_lock.allowed', return_value=False):
            self.assertEqual(self.request('/api/profiles')[0], 423)
