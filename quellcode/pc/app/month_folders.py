"""Local monthly filing and selected-folder exports; attachments are not parsed as readings."""
import base64, datetime, io, json, math, re, time, uuid, zipfile
from pathlib import Path
from diary_actions import visible_rows, export, EXPORT_FILES, HEAD, cells

MONTHS=['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']
def schema(c):
 c.execute('CREATE TABLE IF NOT EXISTS month_assignment(id TEXT PRIMARY KEY,year INTEGER NOT NULL,month INTEGER NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS month_files(id TEXT PRIMARY KEY,year INTEGER NOT NULL,month INTEGER NOT NULL,name TEXT NOT NULL,body BLOB NOT NULL)')

def period(a):
 y=a['year']
 if type(y) is not int or not 1970<=y<=2200:raise ValueError('Jahr ungültig.')
 return y
def month(m):
 if type(m) is not int or not 1<=m<=12:raise ValueError('Monat ungültig.')
 return m
def average(rows):
 def mean(values):return math.floor(sum(values)/len(values)+0.5) if values else None
 pulses=[r['pulse'] for r in rows if r['pulse'] is not None]
 return {'count':len(rows),'pulseCount':len(pulses),'systolic':mean([r['systolic'] for r in rows]),'diastolic':mean([r['diastolic'] for r in rows]),'pulse':mean(pulses)}
def groups(c,year,profile='1'):
 assigned={r['id']:(r['year'],r['month']) for r in c.execute('SELECT * FROM month_assignment')}
 result={m:[] for m in range(1,13)}
 for r in visible_rows(c):
  if str(r.get('profile','1'))!=profile:continue
  dt=datetime.datetime.fromisoformat(r['measuredAt'].replace('Z','+00:00')).astimezone()
  y,m=assigned.get(r['id'],(dt.year,dt.month))
  if y==year:result[m].append(r)
 return result
def overview(c,year,profile='1'):
 g=groups(c,year,profile)
 files=[dict(r) for r in c.execute('SELECT id,month,name,length(body) AS size FROM month_files WHERE year=? ORDER BY name',(year,))]
 return {'months':[{'month':m,'ids':[r['id'] for r in rows],**average(rows),'files':[f for f in files if f['month']==m]} for m,rows in g.items()]}
def summary_table(g,months,year):
 table=[['Zeitraum','Ø SYS mmHg','Ø DIA mmHg','Ø Puls bpm','Messungen','Pulswerte']]
 for label,rows in [(MONTHS[m-1]+' '+str(year),g[m]) for m in months]+[('Gesamtauswahl '+str(year),[r for m in months for r in g[m]])]:
  a=average(rows);table.append([label,a['systolic'] if a['systolic'] is not None else '–',a['diastolic'] if a['diastolic'] is not None else '–',a['pulse'] if a['pulse'] is not None else '–',a['count'],a['pulseCount']])
 return table
def package(c,a):
 year=period(a);months=a['months'];fmt=a['format'];profile=str(a.get('profile','1'))
 if not isinstance(months,list) or not months or len(months)>12 or fmt not in ('pdf','xlsx','csv'):raise ValueError('Bitte Monate und Format wählen.')
 months=sorted(set(month(m) for m in months));g=groups(c,year,profile)
 out=io.BytesIO();total=0
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for m in months:
   folder=f'{year}-{m:02d}-{MONTHS[m-1]}'
   z.writestr(folder+'/',b'')
   if g[m]:z.writestr(folder+'/Messungen.'+fmt,export(g[m],fmt)[0])
   z.writestr(folder+'/Durchschnitt.'+fmt,export([],fmt,summary_table(g,[m],year),MONTHS[m-1]+' - Durchschnitt')[0])
   for f in c.execute('SELECT id,name,body FROM month_files WHERE year=? AND month=?',(year,m)):
    total+=len(f['body'])
    if total>100*1024*1024:raise ValueError('Auswahl größer als 100 MB. Bitte weniger Monate wählen.')
    z.writestr(folder+'/Dateien/'+f['id'][:8]+'_'+f['name'],f['body'])
  if a.get('includeSummary',True):z.writestr('Gesamtdurchschnitt.'+fmt,export([],fmt,summary_table(g,months,year),'Durchschnitt der Monatsauswahl')[0])
  z.writestr('LIESMICH.txt','Durchschnitte aus allen sichtbaren Messungen der ausgewählten Ordner. Jede Messung zählt einmal. Fehlende Pulswerte werden nicht als Null gerechnet. Angefügte Dateien werden unverändert beigelegt und nicht für Durchschnitte ausgewertet.\n')
 return out.getvalue(),f'Blutdruck-{year}-Monatsordner.zip'

def handle(h,connection):
 try:
  size=int(h.headers.get('Content-Length','0'))
  if not 0<size<=22*1024*1024:raise ValueError('Datei zu groß (maximal 15 MB).')
  a=json.loads(h.rfile.read(size))
  with connection() as c:
   schema(c);year=period(a);profile=str(a.get('profile','1'));action=h.path.rsplit('/',1)[-1]
   if profile not in ('1','2','3','4'):raise ValueError('Benutzer ungültig.')
   if action=='list':return h.reply(overview(c,year,profile))
   if action=='assign':
    m=month(a['month']);ids=a['ids']
    if not isinstance(ids,list) or not ids or len(ids)>10000:raise ValueError('Bitte Messungen auswählen.')
    visible={r['id'] for r in visible_rows(c) if str(r.get('profile','1'))==profile}
    if any(not isinstance(id,str) or id not in visible for id in ids):raise ValueError('Messung nicht mehr verfügbar.')
    for id in set(ids):c.execute('INSERT INTO month_assignment VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET year=excluded.year,month=excluded.month',(id,year,m))
   elif action=='upload':
    m=month(a['month']);name=a['name']
    if not isinstance(name,str) or not 1<=len(name)<=160 or re.search(r'[\\/:\x00-\x1f]',name) or name.startswith('.'):raise ValueError('Dateiname ungültig.')
    if Path(name).suffix.lower() not in ('.pdf','.xlsx','.csv'):raise ValueError('Bitte PDF, Excel (xlsx) oder CSV ablegen.')
    body=base64.b64decode(a['data'],validate=True)
    if not 0<len(body)<=15*1024*1024:raise ValueError('Datei zu groß (maximal 15 MB).')
    c.execute('INSERT INTO month_files VALUES(?,?,?,?,?)',(str(uuid.uuid4()),year,m,name,body))
   elif action=='export':
    if a.get('container','zip')=='file':
     fmt=a['format'];months=a['months']
     if fmt not in ('pdf','xlsx','csv') or not isinstance(months,list) or not months or len(months)>12:raise ValueError('Bitte Format und Monate wählen.')
     months=sorted(set(month(m) for m in months));g=groups(c,year,profile);rows=[r for m in months for r in g[m]]
     table=[HEAD]+[cells(r) for r in rows]
     if a.get('includeSummary'):table+=[['']]+summary_table(g,months,year)
     data,kind=export([],fmt,table,'Blutdruck - Monatsauswahl');name=f'Blutdruck-{year}-Auswahl.{fmt}'
    elif a.get('container','zip')=='zip':
     data,name=package(c,a);kind='application/zip'
    else:raise ValueError('Dateityp ungültig.')
    folder=Path(c.execute('PRAGMA database_list').fetchone()[2]).parent/'exports'/str(uuid.uuid4());folder.mkdir(parents=True)
    file=folder/name;file.write_bytes(data);token=str(uuid.uuid4());EXPORT_FILES[token]=(file,time.time())
    return h.reply(data,kind=kind,export_id=token)
   elif action=='file':
    f=c.execute('SELECT name,body FROM month_files WHERE id=? AND year=?',(a['id'],year)).fetchone()
    if not f:raise ValueError('Datei nicht gefunden.')
    kind={'.pdf':'application/pdf','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.csv':'text/csv'}[Path(f['name']).suffix.lower()]
    return h.reply(f['body'],kind=kind)
   else:raise ValueError('Aktion unbekannt.')
  return h.reply({'ok':True})
 except (ValueError,KeyError,TypeError) as e:return h.reply({'error':str(e) or 'Bitte Eingaben prüfen.'},400)
 except OSError:return h.reply({'error':'Datei konnte nicht gespeichert werden.'},500)
