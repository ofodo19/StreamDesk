#!/usr/bin/env python3
"""StreamDesk API as a WSGI app (PythonAnywhere-ready; also runs locally).
Use only streams/playlists you own or are licensed to distribute.

Auth: write routes (POST /api/drafts, /api/publish) require the secret in
env var STREAMDESK_TOKEN, sent as  "Authorization: Bearer <token>"  or
"X-Admin-Token: <token>". If STREAMDESK_TOKEN is unset, writes are disabled.
Reads (GET /api/health, /api/catalogue) stay public so the app can load them.
"""
from pathlib import Path
import datetime, hmac, json, os, threading, uuid

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('STREAMDESK_DATA', ROOT / 'data')); DATA.mkdir(parents=True, exist_ok=True)
CATALOGUE = DATA / 'catalogue.json'; DRAFT = DATA / 'latest-draft.json'
LOCK = threading.Lock()
MAX_BODY = 5_000_000

def load(path, default):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return default

def save(path, obj):
    tmp = path.with_suffix('.tmp')               # atomic write: no half-written JSON
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)

def now(): return datetime.datetime.now().isoformat(timespec='seconds')

def authorized(environ):
    token = os.environ.get('STREAMDESK_TOKEN', '')
    if not token: return None                    # not configured -> writes disabled
    sent = environ.get('HTTP_X_ADMIN_TOKEN', '')
    auth = environ.get('HTTP_AUTHORIZATION', '')
    if auth.lower().startswith('bearer '): sent = auth[7:].strip()
    return hmac.compare_digest(sent.encode(), token.encode())

def application(environ, start_response):
    def send(code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        reason = {200:'OK',201:'Created',204:'No Content',400:'Bad Request',401:'Unauthorized',403:'Forbidden',404:'Not Found',413:'Payload Too Large',500:'Internal Server Error'}.get(code,'OK')
        start_response(f'{code} {reason}', [
            ('Content-Type','application/json; charset=utf-8'), ('Content-Length',str(len(body))),
            ('Access-Control-Allow-Origin','*'),
            ('Access-Control-Allow-Headers','Content-Type, Authorization, X-Admin-Token'),
            ('Access-Control-Allow-Methods','GET,POST,OPTIONS')])
        return [body]

    method, p = environ['REQUEST_METHOD'], environ.get('PATH_INFO', '/')
    if method == 'OPTIONS': return send(204, {})
    if method == 'GET':
        if p == '/api/health': return send(200, {'ok': True, 'service': 'StreamDesk API', 'catalogue_exists': CATALOGUE.exists(), 'writes_enabled': bool(os.environ.get('STREAMDESK_TOKEN'))})
        if p == '/api/catalogue': return send(200, load(CATALOGUE, {'updated_at': None, 'playlists': []}))
        return send(404, {'error': 'Not found'})
    if method != 'POST' or p not in ('/api/drafts', '/api/publish'): return send(404, {'error': 'Not found'})

    ok = authorized(environ)
    if ok is None: return send(403, {'error': 'Writes disabled: set STREAMDESK_TOKEN on the server.'})
    if not ok: return send(401, {'error': 'Missing or invalid token.'})

    try:
        n = int(environ.get('CONTENT_LENGTH') or 0)
        if n < 1 or n > MAX_BODY: return send(413, {'error': 'Request body must be 1 byte to 5 MB'})
        body = json.loads(environ['wsgi.input'].read(n))
        if not isinstance(body, dict): raise ValueError
    except Exception: return send(400, {'error': 'Invalid JSON body'})

    if p == '/api/drafts':
        name = str(body.get('name', 'StreamDesk draft')).strip()[:120]
        channels = body.get('channels', [])
        if not isinstance(channels, list): return send(400, {'error': 'channels must be a list'})
        clean = []
        for ch in channels[:5000]:
            if not isinstance(ch, dict): continue
            url = str(ch.get('url', '')).strip()
            if not (url.startswith('https://') or url.startswith('http://')): continue
            clean.append({'name': str(ch.get('name') or ch.get('title') or 'Channel')[:200], 'url': url, 'type': str(ch.get('type', 'unverified'))[:40]})
        draft = {'id': str(uuid.uuid4()), 'name': name, 'created_at': now(), 'channels': clean, 'status': 'draft', 'rights_confirmed': False}
        with LOCK: save(DRAFT, draft)
        return send(201, {'ok': True, 'draft': draft, 'message': 'Draft saved. Review source rights and test each URL before publishing.'})

    # /api/publish
    if body.get('confirm_rights') is not True: return send(400, {'error': 'Confirm that you own or are authorized to distribute every stream before publishing.'})
    with LOCK:
        draft = load(DRAFT, None)
        if not draft: return send(404, {'error': 'No draft to publish. Create a draft first.'})
        if not draft.get('channels'): return send(400, {'error': 'Draft has no valid URLs.'})
        draft['status'] = 'published'; draft['rights_confirmed'] = True
        cat = load(CATALOGUE, {'updated_at': None, 'playlists': []})
        cat['playlists'] = [x for x in cat.get('playlists', []) if x.get('id') != draft['id']]
        cat['playlists'].insert(0, draft); cat['updated_at'] = now()
        save(CATALOGUE, cat); save(DRAFT, draft)
    return send(200, {'ok': True, 'published': draft, 'catalogue': cat})

if __name__ == '__main__':      # local dev: python streamdesk_server.py
    from wsgiref.simple_server import make_server, WSGIServer
    from socketserver import ThreadingMixIn
    class Threaded(ThreadingMixIn, WSGIServer): daemon_threads = True
    port = int(os.environ.get('STREAMDESK_PORT', '8787'))
    print(f'StreamDesk API on http://0.0.0.0:{port}  (writes {"ENABLED" if os.environ.get("STREAMDESK_TOKEN") else "DISABLED - set STREAMDESK_TOKEN"})')
    make_server('0.0.0.0', port, application, server_class=Threaded).serve_forever()
