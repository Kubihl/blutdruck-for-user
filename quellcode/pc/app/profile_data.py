"""Optional profile data carried by explicitly confirmed measurement imports."""
import datetime
import json
import math


def schema(db):
    db.execute('CREATE TABLE IF NOT EXISTS profile_data(profile TEXT PRIMARY KEY,body TEXT NOT NULL)')


def number(value, low, high):
    if value is None:
        return None
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Ungültige Größe oder ungültiges Gewicht im Profil.')
    return round(value, 1)


def date(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError('Ungültiges Gewichtsdatum.')
    try:
        parsed = datetime.date.fromisoformat(value)
    except ValueError:
        raise ValueError('Ungültiges Gewichtsdatum.') from None
    if parsed > datetime.date.today() or parsed.year < 1900:
        raise ValueError('Ungültiges Gewichtsdatum.')
    return parsed.isoformat()


def validate(raw):
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError('Ungültiges Benutzerprofil.')
    history = raw.get('weightHistory', [])
    if not isinstance(history, list) or len(history) > 5000:
        raise ValueError('Ungültiger Gewichtsverlauf.')
    clean = []
    for item in history:
        if not isinstance(item, dict):
            raise ValueError('Ungültiger Gewichtsverlauf.')
        weight = number(item.get('weightKg'), 20, 400)
        if weight is None:
            raise ValueError('Gewicht im Verlauf fehlt.')
        clean.append({'weightKg': weight, 'date': date(item.get('date'))})
    weight = number(raw.get('weightKg'), 20, 400)
    when = date(raw.get('weightDate'))
    if when and weight is None:
        raise ValueError('Gewicht zum Datum fehlt.')
    if weight is not None:
        clean.append({'weightKg': weight, 'date': when})
    unique = {(v['date'], v['weightKg']): v for v in clean}
    return {'heightCm': number(raw.get('heightCm'), 50, 250), 'weightKg': weight,
            'weightDate': when, 'weightHistory': list(unique.values())}


def read(db, profile):
    schema(db)
    row = db.execute('SELECT body FROM profile_data WHERE profile=?', (profile,)).fetchone()
    return json.loads(row[0]) if row else None


def merge(db, profile, incoming):
    if incoming is None:
        return
    old = read(db, profile) or {'heightCm': None, 'weightKg': None, 'weightDate': None, 'weightHistory': []}
    history = {(v['date'], v['weightKg']): v for v in old['weightHistory'] + incoming['weightHistory']}
    result = dict(old)
    if incoming['heightCm'] is not None:
        result['heightCm'] = incoming['heightCm']
    if incoming['weightKg'] is not None and (not old['weightDate'] or
            incoming['weightDate'] and incoming['weightDate'] >= old['weightDate']):
        result['weightKg'], result['weightDate'] = incoming['weightKg'], incoming['weightDate']
    result['weightHistory'] = sorted(history.values(), key=lambda v: v['date'] or '')
    db.execute('INSERT OR REPLACE INTO profile_data(profile,body) VALUES(?,?)',
               (profile, json.dumps(result, ensure_ascii=False)))
