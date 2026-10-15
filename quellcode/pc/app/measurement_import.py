"""Local, previewed import of selected measurements exported by Puls 180."""
import datetime
import json
import uuid
from profile_data import validate as validate_profile, merge as merge_profile

MAX_BYTES = 2_000_000
MAX_ROWS = 5000


def validate(payload):
    if not isinstance(payload, dict) or payload.get('format') != 'puls180-pc-transfer' or payload.get('version') != 1:
        raise ValueError('Keine Puls-180-Messwertdatei.')
    name = payload.get('profileName')
    rows = payload.get('readings')
    if not isinstance(name, str) or not name.strip() or len(name) > 40 or not isinstance(rows, list) or not 0 < len(rows) <= MAX_ROWS:
        raise ValueError('Name oder Messwertanzahl ungültig.')
    cleaned = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Messwert ungültig.')
        identifier = str(uuid.UUID(row['id']))
        if identifier in seen:
            raise ValueError('Doppelte Kennung in der Datei.')
        seen.add(identifier)
        systolic, diastolic, pulse = row['systolic'], row['diastolic'], row['pulse']
        if type(systolic) is not int or type(diastolic) is not int or not 0 < diastolic < systolic <= 400 or diastolic > 300:
            raise ValueError('Blutdruckwert ungültig.')
        if pulse is not None and (type(pulse) is not int or not 0 < pulse <= 300):
            raise ValueError('Pulswert ungültig.')
        note = row['note']
        if not isinstance(note, str) or len(note) > 1000:
            raise ValueError('Notiz ungültig.')
        when = datetime.datetime.fromisoformat(row['measuredAt'].replace('Z', '+00:00'))
        if when.tzinfo is None or not 0 <= when.timestamp() <= datetime.datetime.now().timestamp() + 300:
            raise ValueError('Messzeit ungültig.')
        cleaned.append((identifier, systolic, diastolic, pulse, when.astimezone(datetime.timezone.utc).isoformat(), note))
    return name.strip(), cleaned


def handle(handler, connection):
    try:
        size = int(handler.headers.get('Content-Length', '0'))
        if not 0 < size <= MAX_BYTES or 'application/json' not in handler.headers.get('Content-Type', ''):
            raise ValueError('Datei zu groß oder falscher Typ.')
        request = json.loads(handler.rfile.read(size))
        source_name, rows = validate(request['package'])
        profile_data = validate_profile(request['package'].get('profileData'))
        profile = str(request.get('profile', ''))
        if profile not in ('1', '2', '3', '4'):
            raise ValueError('Bitte Zielbenutzer wählen.')
        commit = request.get('commit')
        restore_hidden = request.get('restoreHidden', False)
        if type(commit) is not bool or type(restore_hidden) is not bool:
            raise ValueError('Importaktion ungültig.')
        with connection() as db:
            current = db.execute('SELECT name FROM profile_names WHERE profile=?', (profile,)).fetchone()
            if not current:
                raise ValueError('Bitte den PC-Benutzer zuerst benennen.')
            if current[0].casefold() != source_name.casefold():
                raise ValueError('Der Dateiname gehört nicht zum gewählten PC-Benutzer. Bitte passenden Benutzer wählen oder den PC-Namen korrigieren.')
            incoming_ids = {item[0] for item in rows}
            existing = {r['id']: r['profile'] for r in db.execute('SELECT id,profile FROM readings') if r['id'] in incoming_ids}
            conflict = sum(identifier in existing and existing[identifier] != profile for identifier, *_ in rows)
            duplicates = sum(identifier in existing and existing[identifier] == profile for identifier, *_ in rows)
            hidden_ids = {r['id'] for r in db.execute('SELECT id FROM ui_state WHERE hidden=1') if r['id'] in incoming_ids}
            hidden_duplicates = sum(identifier in hidden_ids and existing.get(identifier) == profile for identifier, *_ in rows)
            if conflict:
                raise ValueError(f'{conflict} Messungen gehören bereits einem anderen Benutzer. Nichts importiert.')
            added = 0
            restored = 0
            if commit:
                merge_profile(db, profile, profile_data)
                for row in rows:
                    if row[0] in existing:
                        continue
                    db.execute("INSERT INTO readings(id,systolic,diastolic,pulse,measuredAt,note,origin,profile,profileName) VALUES(?,?,?,?,?,?,'file',?,?)", row + (profile, source_name))
                    added += 1
                if restore_hidden:
                    for identifier, *_ in rows:
                        if identifier in hidden_ids and existing.get(identifier) == profile:
                            restored += db.execute('UPDATE ui_state SET hidden=0 WHERE id=? AND hidden=1', (identifier,)).rowcount
        handler.reply({'sourceName': source_name, 'count': len(rows), 'duplicates': duplicates,
                       'hiddenDuplicates': hidden_duplicates, 'new': len(rows)-duplicates,
                       'added': added, 'restored': restored, 'profile': profile, 'profileData': profile_data})
    except (ValueError, KeyError, TypeError, OverflowError, json.JSONDecodeError) as error:
        handler.reply({'error': str(error) if isinstance(error, ValueError) else 'Ungültige Messwertdatei.'}, 400)
    except Exception:
        handler.reply({'error': 'Import fehlgeschlagen. Es wurden keine Werte geändert.'}, 500)
