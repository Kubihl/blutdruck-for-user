import os,subprocess,time
from pathlib import Path
EXPORT_FILES={}
import json,uuid,io,csv,zipfile,datetime,textwrap
from xml.sax.saxutils import escape

def visible_rows(c,include_hidden=False):
 return [dict(r) for r in c.execute('SELECT r.id,r.systolic,r.diastolic,r.pulse,r.measuredAt,COALESCE(u.note,r.note) AS note,COALESCE(u.hidden,0) AS hidden,r.profile,r.profileName FROM readings r LEFT JOIN ui_state u ON u.id=r.id '+('' if include_hidden else 'WHERE COALESCE(u.hidden,0)=0 ')+'ORDER BY measuredAt DESC')]
def cells(r):
 dt=datetime.datetime.fromisoformat(r['measuredAt'].replace('Z','+00:00')).astimezone()
 hour=dt.hour;part='Morgens' if 5<=hour<12 else 'Mittags' if 12<=hour<17 else 'Abends' if 17<=hour<22 else 'Nachts'
 return [dt.strftime('%d.%m.%Y %H:%M'),r['systolic'],r['diastolic'],r['pulse'] if r['pulse'] is not None else '',part,r['note']]
HEAD=['Datum / Uhrzeit','Systolisch (mmHg)','Diastolisch (mmHg)','Puls (bpm)','Tageszeit','Notiz']
def export(rows,fmt,table_override=None,title=None):
 table=table_override if table_override is not None else [HEAD]+[cells(r) for r in rows]
 if fmt=='csv':
  out=io.StringIO();w=csv.writer(out,delimiter=';')
  for row in table:w.writerow([("'"+v if v.startswith(('=','+','-','@','\t','\r')) else v) if isinstance(v,str) else v for v in row])
  return ('\ufeff'+out.getvalue()).encode(),'text/csv; charset=utf-8'
 if fmt=='xlsx':
  out=io.BytesIO();data=[]
  for i,row in enumerate(table,1):
   cc=[]
   for j,v in enumerate(row):
    ref=chr(65+j)+str(i)
    cc.append(f'<c r="{ref}" s="1"><v>{v}</v></c>' if isinstance(v,(int,float)) else f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>')
   data.append(f'<row r="{i}">'+''.join(cc)+'</row>')
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
   z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
   z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Blutdruck" sheetId="1" r:id="rId1"/></sheets></workbook>')
   z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
   z.writestr('xl/styles.xml','<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="2"><xf/><xf applyAlignment="1"><alignment horizontal="center"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
   z.writestr('xl/worksheets/sheet1.xml','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><cols><col min="1" max="1" width="25" customWidth="1"/><col min="2" max="5" width="23" customWidth="1"/><col min="6" max="6" width="65" customWidth="1"/></cols><sheetData>'+''.join(data)+'</sheetData></worksheet>')
  return out.getvalue(),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
 if fmt!='pdf':raise ValueError()
 # A4, selectable text, explicit WinAnsi font; unsupported glyphs replaced.
 lines=[title or 'Mein Blutdruck - Messliste','Erstellt: '+datetime.datetime.now().astimezone().strftime('%d.%m.%Y %H:%M %Z'),'']
 if table_override is not None:
  for values in table:
   lines.extend(textwrap.wrap(' | '.join(str(v) for v in values),92));lines.append('')
 for r in rows:
  v=cells(r);lines.extend([f'{v[0]} | {v[4]}',f'{v[1]} / {v[2]} mmHg     Puls: {v[3] if v[3]!="" else "-"} bpm'])
  lines.extend(textwrap.wrap(v[5],90));lines.append('')
 pages=[lines[i:i+50] for i in range(0,len(lines),50)]
 objs=[b'',b'',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'];kids=[]
 for page in pages:
  index=len(objs)+1;kids.append(f'{index} 0 R');escaped=[]
  for line in page:escaped.append('('+line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')+') Tj T*')
  stream=('BT /F1 10 Tf 14 TL 40 800 Td '+'\n'.join(escaped)+' ET').encode('cp1252','replace')
  objs.extend([f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {index+1} 0 R >>'.encode(),b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream'])
 objs[0]=b'<< /Type /Catalog /Pages 2 0 R >>';objs[1]=('<< /Type /Pages /Kids ['+' '.join(kids)+f'] /Count {len(kids)} >>').encode();out=bytearray(b'%PDF-1.4\n');offsets=[0]
 for i,obj in enumerate(objs,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 x=len(out);out.extend(f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode());out.extend(''.join(f'{n:010d} 00000 n \n' for n in offsets[1:]).encode());out.extend(f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF'.encode());return bytes(out),'application/pdf'
def handle(h,connection):
 try:
  size=int(h.headers.get('Content-Length','0'))
  if not 0<size<=2000000:raise ValueError()
  a=json.loads(h.rfile.read(size));action=a.get('action');ids=a.get('ids',[])
  if h.path in ('/api/open-with','/api/file-apps','/api/open-app','/api/share-file','/api/save-file'):
   token=a.get('token','');item=EXPORT_FILES.get(token)
   if not item or not item[0].is_file():return h.reply({'error':'Bitte die Datei erneut erzeugen.'},404)
   if os.name!='nt':return h.reply({'error':'Öffnen mit ist nur unter Windows verfügbar.'},400)
   if h.path in ('/api/share-file','/api/save-file'):
    from file_actions import start,status
    mode='save' if h.path=='/api/save-file' else a.get('target')
    return h.reply(status(token,mode) if a.get('poll') else start(token,item[0],mode))
   if h.path=='/api/file-apps':
    from file_apps import applications
    return h.reply({'apps':[{'id':key,'name':app['name']} for key,app in applications(item[0].suffix).items()]})
   if h.path=='/api/open-app':
    from file_apps import launch
    launch(item[0].suffix,a.get('app',''),item[0])
    return h.reply({'ok':True})
   subprocess.Popen([str(Path(__file__).parent/'BlutdruckFileChooser.exe'),str(item[0])],shell=False)
   return h.reply({'ok':True})
  if not isinstance(ids,list) or len(ids)>10000:raise ValueError()
  for id in ids:uuid.UUID(id)
  with connection() as c:
   if h.path=='/api/export':
    rows=[r for r in visible_rows(c) if r['id'] in set(ids)]
    if not rows:raise ValueError()
    data,kind=export(rows,a['format'])
    folder=Path(c.execute('PRAGMA database_list').fetchone()[2]).parent/'exports';folder.mkdir(exist_ok=True)
    token=str(uuid.uuid4());target=folder/token;target.mkdir();file=target/('Blutdruckliste.'+a['format']);file.write_bytes(data);EXPORT_FILES[token]=(file,time.time())
    return h.reply(data,kind=kind,export_id=token)
   if action=='note':
    id=a['id'];uuid.UUID(id);note=a['note']
    if not isinstance(note,str) or len(note)>1000:raise ValueError()
    if not c.execute('SELECT 1 FROM readings WHERE id=?',(id,)).fetchone():raise ValueError()
    c.execute('INSERT INTO ui_state(id,note) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET note=excluded.note',(id,note))
   elif action=='hide':
    if 'expected' in a:
     current={r['id']:r['note'] for r in visible_rows(c)}
     if any(current.get(id)!=a['expected'].get(id) for id in ids):return h.reply({'error':'Notizen wurden inzwischen geändert. Einträge bleiben erhalten.'},409)
    for id in ids:c.execute('INSERT INTO ui_state(id,hidden) VALUES(?,1) ON CONFLICT(id) DO UPDATE SET hidden=1',(id,))
   elif action=='restore':c.execute('UPDATE ui_state SET hidden=0')
   else:raise ValueError()
  return h.reply({'ok':True})
 except OSError:return h.reply({'error':'Datei oder Windows-Programmauswahl konnte nicht geöffnet werden.'},500)
 except (ValueError,KeyError,TypeError):return h.reply({'error':'Bitte Eingaben prüfen.'},400)
