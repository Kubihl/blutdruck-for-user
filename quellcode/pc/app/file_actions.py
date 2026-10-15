import ctypes, subprocess, threading
from pathlib import Path
_processes={}
_lock=threading.Lock()
MODES={'save','email','whatsapp','copy'}

def status(token,mode):
 if mode not in MODES:raise ValueError('Aktion ungültig')
 with _lock:
  process=_processes.get((token,mode))
  if process is None:return {'state':'missing','message':'Bitte die Aktion erneut wählen.'}
  code=process.poll()
 if code is None:return {'state':'pending','message':'Bitte im Zielprogramm fortfahren.'}
 if code==1:return {'state':'cancelled','message':'Abgebrochen. Die Datei bleibt bereit.'}
 if code==31:return {'state':'error','message':'Datei kopiert, WhatsApp konnte nicht gestartet werden. WhatsApp selbst öffnen und im Chat mit Strg+V einfügen oder die Datei speichern.'}
 if code!=0:return {'state':'error','message':'Aktion nicht möglich. Für E-Mail muss ein kompatibles Standard-Mailprogramm eingerichtet sein. Alternativ Datei speichern und dort anhängen.'}
 messages={'save':'Datei gespeichert.','email':'E-Mail-Programm hat die Übergabe abgeschlossen. Den Versand bitte dort prüfen.','copy':'Datei kopiert. Im gewünschten Programm mit Strg+V einfügen.','whatsapp':'Datei kopiert und WhatsApp aufgerufen. Chat wählen und Strg+V drücken. Wenn Einfügen nicht unterstützt wird: Datei speichern und in WhatsApp als Dokument anhängen.'}
 return {'state':'done','message':messages[mode]}

def start(token,file,mode):
 if mode not in MODES:raise ValueError('Aktion ungültig')
 with _lock:
  old=_processes.get((token,mode))
  if old is None or old.poll() is not None:
   # Keep completed results until polled; discard other completed jobs on next action.
   for key in list(_processes):
    if _processes[key].poll() is not None:del _processes[key]
   _processes[(token,mode)]=subprocess.Popen([str(Path(__file__).parent/'BlutdruckDirectActions.exe'),str(file),mode],shell=False)
 return {'state':'pending','message':{'save':'Speicherort wählen.','email':'E-Mail mit Anhang angefordert. Empfänger im Mailprogramm wählen.','whatsapp':'WhatsApp wird aufgerufen. Anschließend Chat wählen und Datei mit Strg+V einfügen.','copy':'Datei wird kopiert.'}[mode]}
