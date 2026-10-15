import json,ssl,threading,ipaddress,socket,secrets,uuid,datetime,html
LAST_SYNC={'connected':False,'device':'','address':'','time':''}
def sync_status():
 try:return json.loads((DATA/'sync-status.json').read_text(encoding='utf-8'))
 except Exception:return dict(LAST_SYNC)
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
ROOT=Path(__file__).parent
from pairing_keys import DATA
import sys,io
sys.path.insert(0,str(ROOT/'vendor'))
import qrcode,qrcode.image.svg
def qr_svg(code):
 qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=6,border=4)
 qr.add_data('BP1|'+code);qr.make(fit=True)
 image=qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
 output=io.BytesIO();image.save(output)
 return output.getvalue().decode().split('?>')[-1]

def config():return json.loads((DATA/'sync.json').read_text())
def pairing_page():
 cfg=config()
 addresses=set()
 try:
  for a in socket.gethostbyname_ex(socket.gethostname())[2]:
   if ipaddress.ip_address(a).is_private and not ipaddress.ip_address(a).is_loopback and not ipaddress.ip_address(a).is_link_local:addresses.add(a)
 except OSError:pass
 boxes=''
 for a in sorted(addresses):
  code=a+'|'+cfg['pin']+'|'+cfg['token']
  boxes+='<h2>'+html.escape(a)+'</h2><div style="background:white;max-width:380px">'+qr_svg(code)+'</div><details><summary>Kopplungscode als Text (alternativ)</summary><textarea readonly rows="4" style="width:100%">'+code+'</textarea></details>'
 return ('<!doctype html><meta charset="utf-8"><title>Handy koppeln</title><style>svg{width:100%;height:auto;display:block}body{background:#f1f5fa;color:#14263f}h1{color:#145bd7}</style><main style="max-width:760px;margin:40px auto;font:20px sans-serif"><h1>Handy mit PC verbinden</h1><p>Beide Geräte müssen im selben WLAN sein. In „Meine App“ oder der Puls 180: Menü → PC-Synchronisierung → QR-Code scannen. Kamerazugriff erlauben und den QR-Code deines Heimnetzes erfassen.</p><p>Der QR-Code koppelt dein Handy mit diesem Tagebuch. Bewahre ihn privat auf. Nutze die Heimnetzadresse (meist 192.168.…), nicht die VPN-Adresse.</p>'+ (boxes or '<p>Keine WLAN-Adresse gefunden. Netzwerkverbindung prüfen.</p>')+'<p>Mit beiden Handy-Apps werden beim Öffnen der Handy-App einmalig Messungen und Handy-Notizen übertragen. PC-Eingaben erscheinen auch auf dem Handy. Ausblenden und Löschen bleiben je Gerät getrennt. Bestehende Messungen werden anhand ihrer Kennung abgeglichen; separat eingegebene Messungen gelten als eigene Einträge.</p><p>Keine Verbindung? Heimnetzadresse statt VPN wählen und erneut scannen. Die Firewall muss das Tagebuch für TCP 18776 im privaten Heimnetz zulassen. Anschließend am PC Aktualisieren drücken.</p><a href="/">Zurück zum Tagebuch</a></main>').encode()

def start(connection, *, test_local=False):
 cfg=config()
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def setup(self):
   super().setup();self.connection.settimeout(15)
  def reply(self,data,status=200):
   body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
  def do_POST(self):
   try:
    n=int(self.headers.get('Content-Length','0'))
    if not 0<n<=2000000:raise ValueError()
    body=self.rfile.read(n)
   except Exception:return self.reply({'error':'Ungültige Anfrage'},400)
   if self.path!='/sync' or self.headers.get('Origin') or not secrets.compare_digest(self.headers.get('Authorization',''),'Bearer '+cfg['token']):return self.reply({'error':'Nicht freigegeben'},403)
   try:
    n=int(self.headers.get('Content-Length','0'))
    if not 0<n<=2000000:raise ValueError()
    data=json.loads(body);rows=data['readings'];profile=str(data.get('profile','1'));profileName=str(data.get('profileName','Benutzer '+profile)).strip()[:40] or 'Benutzer '+profile
    if profile not in ('1','2'):raise ValueError()
    device=str(data.get('device') or 'Handy')[:80]
    if not isinstance(rows,list) or len(rows)>5000:raise ValueError()
    clean=[]
    for r in rows:
     uuid.UUID(r['id'])
     for k,m in [('systolic',400),('diastolic',300)]:
      if type(r[k]) is not int or not 0<r[k]<=m:raise ValueError()
     if r['systolic']<=r['diastolic']:raise ValueError()
     if r['pulse'] is not None and (type(r['pulse']) is not int or not 0<r['pulse']<=300):raise ValueError()
     if not isinstance(r['note'],str) or len(r['note'])>1000:raise ValueError()
     dt=datetime.datetime.fromisoformat(r['measuredAt'].replace('Z','+00:00'))
     if dt.tzinfo is None or not 0<=dt.timestamp()<=datetime.datetime.now().timestamp()+300:raise ValueError()
     clean.append((r['id'],r['systolic'],r['diastolic'],r['pulse'],dt.astimezone(datetime.timezone.utc).isoformat(),r['note'],profile,profileName))
   except Exception:return self.reply({'error':'Ungültige Messdaten'},400)
   try:
    with connection() as c:
     for r in clean:
      c.execute("INSERT INTO readings(id,systolic,diastolic,pulse,measuredAt,note,profile,profileName,origin) VALUES(?,?,?,?,?,?,?,?,'phone') ON CONFLICT(id) DO UPDATE SET note=excluded.note,profile=excluded.profile,profileName=excluded.profileName",r)
     c.execute("INSERT INTO profile_names(profile,name) VALUES(?,?) ON CONFLICT(profile) DO UPDATE SET name=excluded.name",(profile,profileName))
     result=[dict(r) for r in c.execute("SELECT r.* FROM readings r LEFT JOIN ui_state u ON u.id=r.id WHERE r.origin='pc' AND r.profile=? AND COALESCE(u.hidden,0)=0 ORDER BY r.measuredAt DESC LIMIT 5000",(profile,))]
    LAST_SYNC.update({'connected':True,'device':device,'address':self.client_address[0],'time':datetime.datetime.now().astimezone().isoformat(timespec='seconds')})
    (DATA/'sync-status.json').write_text(json.dumps(LAST_SYNC,ensure_ascii=False),encoding='utf-8')
    self.reply({'readings':result,'accepted':len(clean)})
   except Exception:self.reply({'error':'Speichern fehlgeschlagen'},500)
 ports=[18767] if test_local else [18776]
 servers=[]
 context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_2
 context.load_cert_chain(DATA/'sync-cert.pem',DATA/'sync-key.pem')
 for port in ports:
  server=ThreadingHTTPServer(('127.0.0.1' if test_local else '0.0.0.0',port),Handler)
  if not test_local:server.socket=context.wrap_socket(server.socket,server_side=True)
  threading.Thread(target=server.serve_forever,daemon=True).start();servers.append(server)
 if test_local:return servers[0]
 class ServerGroup:
  def shutdown(self):
   for item in servers:item.shutdown()
  def server_close(self):
   for item in servers:item.server_close()
 return ServerGroup()

