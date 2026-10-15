import json,secrets,hashlib,hmac,base64
from pairing_keys import DATA
FILE=DATA/'pc-lock.json'
SESSIONS=set()
def config():
 try:return json.loads(FILE.read_text(encoding='utf-8'))
 except Exception:return {'enabled':False}
def token(headers):
 raw=headers.get('Cookie','')
 for part in raw.split(';'):
  if part.strip().startswith('bp_session='):return part.strip().split('=',1)[1]
 return ''
def allowed(headers):
 c=config();return not c.get('enabled') or token(headers) in SESSIONS
def state(headers):
 c=config();return {'enabled':bool(c.get('enabled')),'unlocked':allowed(headers)}
def verify(pin,c):
 try:
  got=hashlib.pbkdf2_hmac('sha256',pin.encode(),base64.b64decode(c['salt']),200000)
  return hmac.compare_digest(base64.b64encode(got).decode(),c['hash'])
 except Exception:return False
def read(handler):
 n=int(handler.headers.get('Content-Length','0'))
 if not 1<=n<=1024:raise ValueError()
 return json.loads(handler.rfile.read(n))
def handle(handler,path):
 try:data=read(handler);pin=str(data.get('pin',''))
 except Exception:return handler.reply({'error':'Eingabe ungültig.'},400)
 c=config()
 if path=='/api/pin-enable':
  if c.get('enabled'):return handler.reply({'error':'PIN-Sperre ist bereits aktiv.'},409)
  if not pin.isdigit() or not 4<=len(pin)<=12:return handler.reply({'error':'PIN muss aus 4 bis 12 Ziffern bestehen.'},400)
  salt=secrets.token_bytes(16);digest=hashlib.pbkdf2_hmac('sha256',pin.encode(),salt,200000)
  FILE.parent.mkdir(parents=True,exist_ok=True);FILE.write_text(json.dumps({'enabled':True,'salt':base64.b64encode(salt).decode(),'hash':base64.b64encode(digest).decode()}),encoding='utf-8')
 elif path in ['/api/pin-unlock','/api/pin-disable']:
  if not c.get('enabled') or not verify(pin,c):return handler.reply({'error':'PIN ist falsch.'},403)
  if path.endswith('disable'):
   FILE.write_text(json.dumps({'enabled':False}),encoding='utf-8');SESSIONS.clear();return handler.reply({'enabled':False,'unlocked':True})
 elif path=='/api/pin-lock':
  SESSIONS.discard(token(handler.headers));return handler.reply({'enabled':bool(c.get('enabled')),'unlocked':not c.get('enabled')},extra={'Set-Cookie':'bp_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict'})
 else:return handler.reply({'error':'Nicht gefunden'},404)
 session=secrets.token_urlsafe(32);SESSIONS.add(session)
 return handler.reply({'enabled':True,'unlocked':True},extra={'Set-Cookie':'bp_session='+session+'; Path=/; HttpOnly; SameSite=Strict'})