from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import sqlite3,json,uuid,datetime,os,webbrowser,urllib.request
ROOT=Path(__file__).parent
PORT=18775
from pairing_keys import DATA
DB=DATA/'tagebuch.sqlite'
from contextlib import contextmanager
from profile_data import schema as profile_schema, read as read_profile
@contextmanager
def connection():
 DB.parent.mkdir(exist_ok=True)
 c=sqlite3.connect(DB)
 c.execute('CREATE TABLE IF NOT EXISTS readings(id TEXT PRIMARY KEY,systolic INTEGER,diastolic INTEGER,pulse INTEGER,measuredAt TEXT,note TEXT)')
 if 'origin' not in [r[1] for r in c.execute('PRAGMA table_info(readings)')]:c.execute("ALTER TABLE readings ADD COLUMN origin TEXT NOT NULL DEFAULT 'pc'")
 if 'profile' not in [r[1] for r in c.execute('PRAGMA table_info(readings)')]:c.execute("ALTER TABLE readings ADD COLUMN profile TEXT NOT NULL DEFAULT '1'")
 if 'profileName' not in [r[1] for r in c.execute('PRAGMA table_info(readings)')]:c.execute("ALTER TABLE readings ADD COLUMN profileName TEXT NOT NULL DEFAULT 'Benutzer 1'")
 c.execute('CREATE TABLE IF NOT EXISTS ui_state(id TEXT PRIMARY KEY,hidden INTEGER NOT NULL DEFAULT 0,note TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS profile_names(profile TEXT PRIMARY KEY,name TEXT NOT NULL)')
 profile_schema(c)
 c.row_factory=sqlite3.Row
 try:
  yield c
  c.commit()
 except Exception:
  c.rollback();raise
 finally:c.close()
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,data,status=200,kind='application/json; charset=utf-8',download=False,export_id=None,extra=None):
  body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
  if export_id:self.send_header('X-Export-Id',export_id)
  if extra:
   for key,value in extra.items():self.send_header(key,value)
  if download:self.send_header('Content-Disposition','attachment; filename="Blutdruck-Sicherung.json"')
  self.end_headers();self.wfile.write(body)
 def validhost(self):return self.headers.get('Host') in [f'127.0.0.1:{PORT}',f'localhost:{PORT}']
 def do_GET(self):
  if not self.validhost():return self.reply({'error':'Ungültiger Zugriff'},403)
  if self.path=='/api/identity':return self.reply({'app':'blutdruck-sales-desktop','version':'5.12'})
  if self.path=='/api/pin-status':
   from pc_lock import state
   return self.reply(state(self.headers))
  from pc_lock import allowed
  if (self.path=='/pair' or self.path.startswith('/api/')) and not allowed(self.headers):return self.reply({'error':'PC-Tagebuch gesperrt'},423)
  if self.path=='/api/pc-update':
   try:
    request=urllib.request.Request('https://raw.githubusercontent.com/Kubihl/blutdruck-for-user/main/pc-version.json?ts='+str(int(datetime.datetime.now().timestamp())),headers={'User-Agent':'Puls-180-PC-Tagebuch/5.12'})
    with urllib.request.urlopen(request,timeout=6) as response:return self.reply(json.load(response))
   except Exception:
    try:
     request=urllib.request.Request('https://raw.githubusercontent.com/Kubihl/blutdruck-for-user/main/version.json?ts='+str(int(datetime.datetime.now().timestamp())),headers={'User-Agent':'Puls-180-PC-Tagebuch/5.12'})
     with urllib.request.urlopen(request,timeout=6) as response:data=json.load(response)
     return self.reply({'versionCode':data.get('pcDiaryVersionCode',60),'versionName':data.get('pcDiaryVersionName','5.12'),'zipUrl':data.get('pcDiaryUrl','')})
    except Exception:return self.reply({'error':'Internetverbindung prüfen.'},503)
  if self.path=='/api/sync-status':return self.reply({'connected':False,'mode':'file'})
  if self.path=='/api/profiles':
   with connection() as c:
    names={'1':'Benutzer 1','2':'Benutzer 2','3':'Benutzer 3','4':'Benutzer 4'}
    names.update({r['profile']:r['profileName'] for r in c.execute('SELECT profile,profileName FROM readings ORDER BY measuredAt')})
    names.update({r['profile']:r['name'] for r in c.execute('SELECT profile,name FROM profile_names')})
    return self.reply({'profiles':[{'profile':profile,'name':name,'profileData':read_profile(c,profile)} for profile,name in sorted(names.items())]})
  if self.path in ['/api/measurements','/api/backup']:
   from diary_actions import visible_rows
   with connection() as c:
    rows=visible_rows(c,include_hidden=self.path=='/api/backup')
    names={'1':'Benutzer 1','2':'Benutzer 2','3':'Benutzer 3','4':'Benutzer 4'}
    names.update({r['profile']:r['profileName'] for r in c.execute('SELECT profile,profileName FROM readings ORDER BY measuredAt')})
    names.update({r['profile']:r['name'] for r in c.execute('SELECT profile,name FROM profile_names')})
    data={'readings':rows,'profiles':[{'profile':profile,'name':name,'profileData':read_profile(c,profile)} for profile,name in sorted(names.items())]}
    if self.path=='/api/backup':
     from month_folders import schema
     import base64
     schema(c);data['monthAssignments']=[dict(r) for r in c.execute('SELECT * FROM month_assignment')]
     data['monthFiles']=[{**dict(r),'body':base64.b64encode(r['body']).decode()} for r in c.execute('SELECT * FROM month_files')]
   return self.reply(data,download=self.path=='/api/backup')
  names={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/datenschutz.html':'datenschutz.html','/anleitung.html':'anleitung.html','/anleitung.pdf':'anleitung.pdf','/vergleich.html':'vergleich.html','/vergleich.js':'vergleich.js','/import.html':'import.html','/import.js':'import.js','/benutzer.html':'benutzer.html','/benutzer.js':'benutzer.js','/front-user.js':'front-user.js','/status.js':'status.js'}
  if self.path not in names:return self.reply({'error':'Nicht gefunden'},404)
  file=ROOT/'web'/names[self.path];kind='text/html' if file.suffix=='.html' else 'text/css' if file.suffix=='.css' else 'application/pdf' if file.suffix=='.pdf' else 'text/javascript'
  self.reply(file.read_bytes(),kind=kind+'; charset=utf-8')
 def do_POST(self):
  if not self.validhost() or self.headers.get('Origin') not in [f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}']:return self.reply({'error':'Ungültiger Ursprung'},403)
  if self.path=='/api/open-bluetooth':
   try: os.startfile('ms-settings:bluetooth'); return self.reply({'message':'Windows-Bluetooth wurde geöffnet.'})
   except Exception: return self.reply({'error':'Windows-Bluetooth konnte nicht geöffnet werden.'},500)
  if self.path.startswith('/api/pin-'):
   from pc_lock import handle
   return handle(self,self.path)
  from pc_lock import allowed
  if not allowed(self.headers):return self.reply({'error':'PC-Tagebuch gesperrt'},423)
  if self.path=='/api/profile-data':
   from profile_edit import handle
   return handle(self,connection)
  if self.path=='/api/profile-name':
   try:
    n=int(self.headers.get('Content-Length','0'))
    if not 0<n<=500:raise ValueError('Ungültige Eingabe.')
    payload=json.loads(self.rfile.read(n))
    profile=str(payload.get('profile',''))
    name=payload.get('name')
    if profile not in ('1','2','3','4') or not isinstance(name,str) or not 1<=len(name.strip())<=40 or any(ord(ch)<32 for ch in name):raise ValueError('Bitte einen Namen mit höchstens 40 Zeichen eingeben.')
    name=name.strip()
    with connection() as c:
     others=c.execute('SELECT name FROM profile_names WHERE profile<>?',(profile,)).fetchall()
     if any(row['name'].casefold()==name.casefold() for row in others):raise ValueError('Dieser Name gehört bereits zu einem anderen Benutzer.')
     c.execute('INSERT OR REPLACE INTO profile_names(profile,name) VALUES(?,?)',(profile,name))
    return self.reply({'profile':profile,'name':name})
   except (ValueError,TypeError,KeyError,json.JSONDecodeError) as error:return self.reply({'error':str(error)},400)
  if self.path=='/api/measurement-import':
   from measurement_import import handle
   return handle(self,connection)
  if self.path.startswith('/api/months/'):
   from month_folders import handle
   return handle(self,connection)
  if self.path in ['/api/action','/api/export','/api/open-with','/api/file-apps','/api/open-app','/api/share-file','/api/save-file']:
   from diary_actions import handle
   return handle(self,connection)
  if self.path!='/api/measurements':return self.reply({'error':'Nicht gefunden'},404)
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<=6000 or 'application/json' not in self.headers.get('Content-Type',''):raise ValueError()
   a=json.loads(self.rfile.read(n));uuid.UUID(a['id'])
   for key,maximum in [('systolic',400),('diastolic',300)]:
    if type(a[key]) is not int or not 1<=a[key]<=maximum:raise ValueError()
   if a['systolic']<=a['diastolic']:raise ValueError()
   if a['pulse'] is not None and (type(a['pulse']) is not int or not 1<=a['pulse']<=300):raise ValueError()
   if not isinstance(a['note'],str) or len(a['note'])>1000:raise ValueError()
   if str(a.get('profile','1')) not in ('1','2','3','4'):raise ValueError()
   a['profile']=str(a.get('profile','1'));a['profileName']=str(a.get('profileName','Benutzer '+a['profile'])).strip()[:40] or 'Benutzer '+a['profile']
   dt=datetime.datetime.fromisoformat(a['measuredAt'].replace('Z','+00:00'))
   if dt.tzinfo is None or dt.timestamp()<0 or dt.timestamp()>datetime.datetime.now().timestamp()+300:raise ValueError()
   a['measuredAt']=dt.astimezone(datetime.timezone.utc).isoformat()
  except Exception:return self.reply({'error':'Bitte Eingaben prüfen.'},400)
  try:
   with connection() as c:c.execute('INSERT OR IGNORE INTO readings(id,systolic,diastolic,pulse,measuredAt,note,profile,profileName) VALUES(?,?,?,?,?,?,?,?)',tuple(a[k] for k in ['id','systolic','diastolic','pulse','measuredAt','note','profile','profileName']))
   self.reply({'id':a['id']},201)
  except sqlite3.Error:self.reply({'error':'Speichern fehlgeschlagen.'},500)
if __name__=='__main__':
 ThreadingHTTPServer.allow_reuse_address=False
 try:server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
 except OSError:
  if '--open' in __import__('sys').argv:webbrowser.open(f'http://127.0.0.1:{PORT}')
  raise SystemExit()
 if '--open' in __import__('sys').argv:webbrowser.open(f'http://127.0.0.1:{PORT}')
 with connection():pass
 server.serve_forever()




