from contextlib import closing
import base64
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import server
import backup_restore as br
from diary_actions import visible_rows

class RestoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name)/'test.sqlite'
        self.patcher = patch.object(server,'DB',self.db)
        self.patcher.start(); self.addCleanup(self.patcher.stop)
        br.PENDING.clear()
        with server.connection() as c:
            br.schema(c)
            c.execute("INSERT INTO readings(id,systolic,diastolic,pulse,measuredAt,note) VALUES('old',120,80,60,'2026-01-01T12:00:00+01:00','alt')")
        self.data = {'readings':[{'id':'new','systolic':124,'diastolic':75,'pulse':None,'measuredAt':'2026-11-21T14:58:00+01:00','note':'Notiz ä','profile':'2','profileName':'Test 2','hidden':1}],
          'profiles':[{'profile':str(i),'name':'Test '+str(i),'profileData':None} for i in range(1,5)],
          'monthAssignments':[{'id':'new','year':2026,'month':11}],
          'monthFiles':[{'id':'file','year':2026,'month':11,'name':'probe.txt','body':base64.b64encode(b'example').decode()}]}
    def preview(self):
        with server.connection() as c: return br.preview(c,self.data)
    def test_roundtrip_and_previous_snapshot(self):
        preview=self.preview()
        with server.connection() as c:
            self.assertEqual(c.execute('SELECT id FROM readings').fetchone()[0],'old')
            result=br.restore(c,self.db,preview['token'])
        with server.connection() as c:
            self.assertEqual(visible_rows(c),[])
            self.assertEqual(visible_rows(c,True)[0]['note'],'Notiz ä')
            self.assertEqual(c.execute('SELECT body FROM month_files').fetchone()[0],b'example')
            self.assertEqual(c.execute('SELECT count(*) FROM profile_names').fetchone()[0],4)
        with closing(sqlite3.connect(result['backup'])) as c:
            self.assertEqual(c.execute('SELECT id FROM readings').fetchone()[0],'old')
        with server.connection() as c:
            with self.assertRaises(ValueError): br.restore(c,self.db,preview['token'])
    def test_invalid_backup_changes_nothing(self):
        for mutate in (lambda d:d['readings'].append(copy.deepcopy(d['readings'][0])),
                       lambda d:d['readings'][0].update(systolic=999),
                       lambda d:d['monthFiles'][0].update(body='%%%'),
                       lambda d:d.pop('profiles')):
            data=copy.deepcopy(self.data); mutate(data)
            with server.connection() as c:
                before=br.fingerprint(c)
                with self.assertRaises((ValueError,KeyError)): br.preview(c,data)
                self.assertEqual(br.fingerprint(c),before)
    def test_change_after_preview_rejected(self):
        token=self.preview()['token']
        with server.connection() as c: c.execute("UPDATE readings SET note='changed'")
        with server.connection() as c:
            with self.assertRaises(ValueError): br.restore(c,self.db,token)
            self.assertEqual(c.execute('SELECT note FROM readings').fetchone()[0],'changed')
    def test_failure_rolls_back(self):
        token=self.preview()['token']
        with server.connection() as c:
            before=br.fingerprint(c)
            c.execute("CREATE TRIGGER fail_insert BEFORE INSERT ON readings BEGIN SELECT RAISE(ABORT,'test'); END")
        with server.connection() as c:
            with self.assertRaises(sqlite3.Error): br.restore(c,self.db,token)
            self.assertEqual(br.fingerprint(c),before)
    def test_http_confirmation_required(self):
        h=object.__new__(server.Handler)
        h.headers={'Content-Type':'application/json'}
        import io
        raw=json.dumps({'action':'restore','token':'unused'}).encode()
        h.headers['Content-Length']=str(len(raw)); h.rfile=io.BytesIO(raw)
        h.reply=lambda data,status=200:(status,data)
        self.assertEqual(br.handle(h,server.connection,self.db)[0],400)

if __name__ == '__main__': unittest.main()
