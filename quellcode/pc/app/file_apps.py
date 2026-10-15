"""Discover locally registered file applications; never accept executable paths from clients."""
import ctypes, hashlib, os, subprocess
from pathlib import Path
import winreg as w

def values(hive,key):
 try:
  with w.OpenKey(hive,key) as k:
   return [w.EnumValue(k,i)[:2] for i in range(w.QueryInfoKey(k)[1])]
 except OSError:return []
def value(hive,key,name=''):
 return dict(values(hive,key)).get(name,'')
def applications(ext):
 if ext not in ('.pdf','.xlsx','.csv','.zip'):return {}
 progs=set(n for n,v in values(w.HKEY_CLASSES_ROOT,ext+r'\OpenWithProgids'))
 base=r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts'+chr(92)+ext
 progs.update(n for n,v in values(w.HKEY_CURRENT_USER,base+r'\OpenWithProgids'))
 progs.add(value(w.HKEY_CLASSES_ROOT,ext))
 progs.add(value(w.HKEY_CURRENT_USER,base+r'\UserChoice','ProgId'))
 exes={v for n,v in values(w.HKEY_CURRENT_USER,base+r'\OpenWithList') if n!='MRUList' and isinstance(v,str) and v.lower().endswith('.exe')}
 progs.update('Applications\\'+exe for exe in exes)
 result={}
 for prog in sorted(p for p in progs if isinstance(p,str) and p):
  command=value(w.HKEY_CLASSES_ROOT,prog+r'\shell\open\command')
  if not isinstance(command,str) or not command:continue
  parser=ctypes.windll.shell32.CommandLineToArgvW
  parser.restype=ctypes.POINTER(ctypes.c_wchar_p)
  parser.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int)]
  count=ctypes.c_int();argv=parser(os.path.expandvars(command),ctypes.byref(count))
  if not argv:continue
  try:exe=argv[0]
  finally:
   ctypes.windll.kernel32.LocalFree.argtypes=[ctypes.c_void_p]
   ctypes.windll.kernel32.LocalFree(argv)
  if not os.path.isabs(exe):
   exe=next((value(h,r'Software\Microsoft\Windows\CurrentVersion\App Paths'+chr(92)+exe) for h in (w.HKEY_CURRENT_USER,w.HKEY_LOCAL_MACHINE) if value(h,r'Software\Microsoft\Windows\CurrentVersion\App Paths'+chr(92)+exe)),exe)
  path=Path(exe)
  if not path.is_file() or path.suffix.lower()!='.exe':continue
  # Only directly executable applications, not shell/COM launch commands.
  if path.name.lower() in ('rundll32.exe','cmd.exe','powershell.exe','wscript.exe','cscript.exe','explorer.exe'):continue
  label={'msedge.exe':'Microsoft Edge','pdfelement.exe':'Wondershare PDFelement','winword.exe':'Microsoft Word','excel.exe':'Microsoft Excel','easypdf.exe':'EasyPDF'}.get(path.name.lower(),path.stem)
  key=hashlib.sha256(str(path).lower().encode()).hexdigest()[:24]
  result[key]={'name':label,'path':str(path)}
 if ext=='.zip':
  explorer=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'explorer.exe'
  if explorer.is_file():result['windows-explorer']={'name':'Windows-Explorer (ZIP-Ordner)','path':str(explorer)}
 return result

def launch(ext,app_id,file):
 app=applications(ext).get(app_id)
 if not app:raise ValueError('Programm nicht mehr verfügbar. Bitte Auswahl neu öffnen.')
 subprocess.Popen([app['path'],str(file)],shell=False)
