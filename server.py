from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, subprocess, os
ROOT=Path(__file__).resolve().parent
DATA_DIR=Path(os.environ.get('GUIWEI_DATA_DIR', str(Path.home()/'Library/Application Support/Guiwei')))
DATA_DIR.mkdir(parents=True,exist_ok=True)
DATA=DATA_DIR/'tasks.json'
LOCK=__import__('threading').Lock()
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def reply(self,status,data,kind='application/json'):
  body=data.encode() if isinstance(data,str) else json.dumps(data,ensure_ascii=False).encode()
  self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
 def do_GET(self):
  if self.path=='/': return self.reply(200,(ROOT/'index.html').read_text(),'text/html')
  if self.path=='/api/state':
   try:
    tasks=json.loads(DATA.read_text()) if DATA.exists() else []
    groups=json.loads((DATA_DIR/'folders.json').read_text()) if (DATA_DIR/'folders.json').exists() else {}
    folders=[{'name':n,'group':groups.get(n,'library')} for n in sorted(os.listdir(Path.home()/'Desktop')) if (Path.home()/'Desktop'/n).is_dir() and not n.startswith('.')]
    return self.reply(200,{'tasks':tasks,'folders':folders})
   except Exception: return self.reply(500,{'error':'无法读取本地数据，请检查文件权限'})
  self.reply(404,{})
 def do_POST(self):
  if self.headers.get('Origin') not in (None,'http://127.0.0.1:18743'): return self.reply(403,{})
  if self.headers.get('Content-Type')!='application/json': return self.reply(415,{})
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size>1000000: return self.reply(413,{})
   body=json.loads(self.rfile.read(size))
   if self.path=='/api/tasks':
    if not isinstance(body,list) or any(not isinstance(t,dict) or not isinstance(t.get('text'),str) or len(t['text'])>1000 or t.get('q') not in ['inbox','do','plan','delegate','later'] for t in body): return self.reply(400,{})
    with LOCK:
     tmp=DATA.with_suffix('.tmp'); tmp.write_text(json.dumps(body,ensure_ascii=False,indent=2)); tmp.replace(DATA)
   elif self.path=='/api/open':
    name=body['name']; target=Path.home()/'Desktop'/name
    if name!=Path(name).name or not target.is_dir(): return self.reply(400,{})
    subprocess.Popen(['/usr/bin/open',str(target)])
   elif self.path=='/api/group':
    name=body['name']; group=body['group']
    if group not in ['work','projects','library'] or name!=Path(name).name: return self.reply(400,{})
    f=DATA_DIR/'folders.json'; groups=json.loads(f.read_text()) if f.exists() else {}; groups[name]=group
    tmp=f.with_suffix('.tmp'); tmp.write_text(json.dumps(groups,ensure_ascii=False,indent=2)); tmp.replace(f)
   else: return self.reply(404,{})
   self.reply(200,{'ok':True})
  except Exception: self.reply(500,{'error':'操作失败，请重试'})
if __name__ == '__main__':
 ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('GUIWEI_PORT','18743'))),Handler).serve_forever()
