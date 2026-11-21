"""Explicit, previewed replacement of diary data with a validated JSON backup."""
from contextlib import closing
import base64
import datetime
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from profile_data import validate as validate_profile
from month_folders import schema

PENDING = {}
LOCK = threading.Lock()
TABLES = ('readings', 'ui_state', 'profile_names', 'profile_data', 'month_assignment', 'month_files')

def text(value, limit):
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError('Ungültiger Text in der Sicherung.')
    return value

def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Ungültige Zahl in der Sicherung.')
    return value

def validate(data):
    if not isinstance(data, dict) or not all(k in data for k in ('readings', 'profiles', 'monthAssignments', 'monthFiles')):
        raise ValueError('Bitte eine vollständige PC-Tagebuch-Sicherung wählen, keine Handydatei.')
    for key in ('readings', 'profiles', 'monthAssignments', 'monthFiles'):
        if not isinstance(data[key], list) or len(data[key]) > 100000:
            raise ValueError('Ungültige oder zu große Sicherung.')
    profiles = []
    slots = set()
    names = set()
    for p in data['profiles']:
        slot = str(p['profile'])
        name = text(p['name'], 40)
        if slot not in ('1','2','3','4') or slot in slots or not name.strip() or name.casefold() in names:
            raise ValueError('Ungültige oder doppelte Benutzer.')
        slots.add(slot); names.add(name.casefold())
        profiles.append((slot, name, validate_profile(p.get('profileData'))))
    if slots != {'1','2','3','4'}:
        raise ValueError('Die Sicherung muss alle vier Benutzer enthalten.')
    readings = []
    ids = set()
    for r in data['readings']:
        rid = text(r['id'], 300)
        if not rid or rid in ids or str(r['profile']) not in slots:
            raise ValueError('Doppelte Messung oder unbekannter Benutzer.')
        ids.add(rid)
        date = text(r['measuredAt'], 80)
        parsed = datetime.datetime.fromisoformat(date.replace('Z', '+00:00'))
        if parsed.tzinfo is None or not 1900 <= parsed.year <= 2200:
            raise ValueError('Ungültiger Messzeitpunkt.')
        pulse = r.get('pulse')
        if pulse is not None: integer(pulse, 1, 400)
        hidden = r.get('hidden', 0)
        if hidden not in (0,1) or type(hidden) not in (int,bool):
            raise ValueError('Ungültiger Ausblendestatus.')
        readings.append((rid, integer(r['systolic'],1,400), integer(r['diastolic'],1,300), pulse,
                         date, text(r.get('note') or '',10000), str(r['profile']),
                         text(r['profileName'],40), int(hidden)))
    assignments = []
    seen = set()
    for a in data['monthAssignments']:
        rid = a['id']
        if rid not in ids or rid in seen: raise ValueError('Ungültige Monatszuordnung.')
        seen.add(rid)
        assignments.append((rid,integer(a['year'],1970,2200),integer(a['month'],1,12)))
    files = []
    seen = set()
    size = 0
    for f in data['monthFiles']:
        fid = text(f['id'],300)
        if not fid or fid in seen: raise ValueError('Doppelte Monatsdatei.')
        seen.add(fid)
        body = base64.b64decode(f['body'],validate=True)
        size += len(body)
        if size > 30*1024*1024: raise ValueError('Anhänge sind zu groß.')
        files.append((fid,integer(f['year'],1970,2200),integer(f['month'],1,12),text(f['name'],500),body))
    return {'readings': readings, 'profiles': profiles, 'assignments': assignments, 'files': files}

def fingerprint(c):
    digest = hashlib.sha256()
    for table in TABLES:
        rows = [tuple(r) for r in c.execute('SELECT * FROM '+table+' ORDER BY 1')]
        digest.update(repr(rows).encode('utf-8'))
    return digest.hexdigest()

def preview(c, data):
    clean = validate(data)
    schema(c)
    token = secrets.token_urlsafe(32)
    current = c.execute('SELECT count(*) FROM readings').fetchone()[0]
    with LOCK:
        now = time.monotonic()
        for key in list(PENDING):
            if now-PENDING[key][0] > 600: del PENDING[key]
        if len(PENDING) >= 8: raise ValueError('Zu viele Vorschauen. Bitte später erneut versuchen.')
        PENDING[token] = (now, clean, fingerprint(c))
    return {'token': token, 'current': current, 'count': len(clean['readings']),
            'hidden': sum(r[-1] for r in clean['readings']), 'files': len(clean['files']),
            'profiles': [p[1] for p in clean['profiles']]}

def restore(c, db_path, token):
    with LOCK:
        pending = PENDING.pop(token, None)
    if not pending or time.monotonic()-pending[0] > 600:
        raise ValueError('Vorschau abgelaufen. Bitte die Datei erneut prüfen.')
    _, data, expected = pending
    c.commit()
    c.execute('BEGIN IMMEDIATE')
    try:
        if fingerprint(c) != expected:
            raise ValueError('Die Daten haben sich geändert. Bitte eine neue Vorschau öffnen.')
        folder = Path(db_path).parent/'Sicherungen-vor-Wiederherstellung'
        folder.mkdir(parents=True,exist_ok=True)
        snapshot = folder/('Tagebuch-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+secrets.token_hex(4)+'.sqlite')
        with closing(sqlite3.connect(db_path)) as source, closing(sqlite3.connect(snapshot)) as target:
            source.backup(target)
        for table in TABLES: c.execute('DELETE FROM '+table)
        for r in data['readings']:
            c.execute('INSERT INTO readings(id,systolic,diastolic,pulse,measuredAt,note,profile,profileName,origin) VALUES(?,?,?,?,?,?,?,?,?)',r[:8]+('pc',))
            c.execute('INSERT INTO ui_state(id,hidden,note) VALUES(?,?,?)',(r[0],r[8],r[5]))
        for slot,name,profile in data['profiles']:
            c.execute('INSERT INTO profile_names(profile,name) VALUES(?,?)',(slot,name))
            if profile is not None:
                c.execute('INSERT INTO profile_data(profile,body) VALUES(?,?)',(slot,json.dumps(profile,ensure_ascii=False)))
        c.executemany('INSERT INTO month_assignment(id,year,month) VALUES(?,?,?)',data['assignments'])
        c.executemany('INSERT INTO month_files(id,year,month,name,body) VALUES(?,?,?,?,?)',data['files'])
        c.commit()
        return {'count':len(data['readings']), 'backup':str(snapshot)}
    except Exception:
        c.rollback()
        raise

def handle(h, connection, db_path):
    try:
        length = int(h.headers.get('Content-Length','0'))
        if not 0 < length <= 40*1024*1024 or 'application/json' not in h.headers.get('Content-Type',''):
            raise ValueError('Sicherungsdatei fehlt oder ist zu groß (maximal 40 MB).')
        payload = json.loads(h.rfile.read(length))
        with connection() as c:
            if payload.get('action') == 'preview': return h.reply(preview(c,payload['data']))
            if payload.get('action') == 'restore' and payload.get('confirmed') is True:
                return h.reply(restore(c,db_path,payload['token']))
            raise ValueError('Bitte zuerst Vorschau prüfen und Wiederherstellung bestätigen.')
    except (ValueError,TypeError,KeyError,AttributeError) as error:
        return h.reply({'error':str(error)},400)
    except (OSError,sqlite3.Error):
        return h.reply({'error':'Wiederherstellung fehlgeschlagen. Der bisherige Datenbestand bleibt erhalten.'},500)
