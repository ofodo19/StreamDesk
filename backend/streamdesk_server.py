#!/usr/bin/env python3
"""Local StreamDesk demo API. Use only streams/playlists you own or are licensed to distribute."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json, os, threading, uuid
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
CATALOGUE=DATA/'catalogue.json'; DRAFT=DATA/'latest-draft.json'
LOCK=threading.Lock()
def load(path, default):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return default
def save(path, obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
class Handler(BaseHTTPRequestHandler):
    def send_json(self,code,obj):
        b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS'); self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self): self.send_json(204,{})
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/health': return self.send_json(200,{'ok':True,'service':'StreamDesk demo API','catalogue_exists':CATALOGUE.exists()})
        if p=='/api/catalogue': return self.send_json(200,load(CATALOGUE,{'updated_at':None,'playlists':[]}))
        return self.send_json(404,{'error':'Not found'})
    def do_POST(self):
        p=urlparse(self.path).path
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<1 or n>5_000_000: return self.send_json(413,{'error':'Request body must be 1 byte to 5 MB'})
            body=json.loads(self.rfile.read(n))
        except Exception: return self.send_json(400,{'error':'Invalid JSON body'})
        if p=='/api/drafts':
            # Accept a reviewed playlist payload; do not scrape third-party sites in this server.
            name=str(body.get('name','StreamDesk draft')).strip()[:120]
            channels=body.get('channels',[])
            if not isinstance(channels,list): return self.send_json(400,{'error':'channels must be a list'})
            clean=[]
            for ch in channels[:5000]:
                if not isinstance(ch,dict): continue
                url=str(ch.get('url','')).strip()
                if not (url.startswith('https://') or url.startswith('http://')): continue
                clean.append({'name':str(ch.get('name') or ch.get('title') or 'Channel')[:200],'url':url,'type':str(ch.get('type','unverified'))[:40]})
            draft={'id':str(uuid.uuid4()),'name':name,'created_at':__import__('datetime').datetime.now().isoformat(timespec='seconds'),'channels':clean,'status':'draft','rights_confirmed':False}
            with LOCK: save(DRAFT,draft)
            return self.send_json(201,{'ok':True,'draft':draft,'message':'Draft saved. Review source rights and test each URL before publishing.'})
        if p=='/api/publish':
            if body.get('confirm_rights') is not True: return self.send_json(400,{'error':'Confirm that you own or are authorized to distribute every stream before publishing.'})
            draft=load(DRAFT,None)
            if not draft: return self.send_json(404,{'error':'No draft to publish. Create a draft first.'})
            if not draft.get('channels'): return self.send_json(400,{'error':'Draft has no valid URLs.'})
            draft['status']='published'; draft['rights_confirmed']=True
            cat=load(CATALOGUE,{'updated_at':None,'playlists':[]})
            cat['playlists']=[p for p in cat.get('playlists',[]) if p.get('id')!=draft['id']]
            cat['playlists'].insert(0,draft)
            cat['updated_at']=__import__('datetime').datetime.now().isoformat(timespec='seconds')
            with LOCK: save(CATALOGUE,cat); save(DRAFT,draft)
            return self.send_json(200,{'ok':True,'published':draft,'catalogue':cat})
        return self.send_json(404,{'error':'Not found'})
    def log_message(self,fmt,*args): print('[StreamDesk API] '+fmt%args)
if __name__=='__main__':
    port=int(os.environ.get('STREAMDESK_PORT','8787'))
    print(f'StreamDesk API running at http://127.0.0.1:{port}')
    print('Demo only: no authentication. Do not expose to the public internet.')
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
