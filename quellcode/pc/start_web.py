from pathlib import Path
import urllib.request,json,subprocess,time,webbrowser
root=Path(__file__).resolve().parent
url='http://127.0.0.1:18775/'
def ready():
 try:
  with urllib.request.urlopen(url+'api/identity',timeout=1) as response:data=json.load(response);return data.get('app')=='blutdruck-sales-desktop' and data.get('version')=='5.12'
 except Exception:return False
if not ready():
 subprocess.Popen([str(root/'runtime/pythonw.exe'),str(root/'app/server.py')],cwd=root/'app',creationflags=0x08000000)
 for _ in range(60):
  if ready():break
  time.sleep(.25)
if ready():webbrowser.open(url)
else:raise SystemExit('Tagebuch 5.12 konnte nicht starten. Falls eine alte Tagebuch-Version laeuft, zuerst deren Hintergrundserver beenden. Port 18775 und Schutzprogramm-Meldungen pruefen. Schutz nicht deaktivieren.')
