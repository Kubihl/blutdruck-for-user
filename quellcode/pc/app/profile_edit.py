"""Explicit local profile edits, scoped to one user."""
import json
from profile_data import validate, read


def handle(handler, connection):
    try:
        size = int(handler.headers.get('Content-Length', '0'))
        if not 0 < size <= 2000:
            raise ValueError('Ungültige Eingabe.')
        data = json.loads(handler.rfile.read(size))
        if not isinstance(data, dict) or data.get('profile') not in ('1', '2', '3', '4'):
            raise ValueError('Ungültiger Benutzer.')
        profile = data['profile']
        incoming = validate(data.get('profileData'))
        if incoming is None:
            raise ValueError('Profilangaben fehlen.')
        with connection() as db:
            old = read(db, profile) or {}
            history = old.get('weightHistory', []) + incoming['weightHistory']
            incoming['weightHistory'] = sorted(
                {(item['date'], item['weightKg']): item for item in history}.values(),
                key=lambda item: item['date'] or '')
            db.execute('INSERT OR REPLACE INTO profile_data(profile,body) VALUES(?,?)',
                       (profile, json.dumps(incoming, ensure_ascii=False)))
        return handler.reply({'profile': profile, 'profileData': incoming})
    except (ValueError, TypeError, KeyError) as error:
        return handler.reply({'error': str(error)}, 400)
