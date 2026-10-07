#!/usr/bin/env python3
"""python3 server.py  →  http://localhost:8000  (새로고침할 때마다 폴더를 다시 읽음)"""
import json, os, re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.heic')

def load_houses():
    houses = []
    for name in os.listdir(ROOT):
        d = os.path.join(ROOT, name)
        if not os.path.isdir(d) or name.startswith('.'):
            continue
        files = sorted(os.listdir(d))
        imgs = [f for f in files if f.lower().endswith(IMG)]
        map_img = next((f for f in imgs if os.path.splitext(f)[0].lower() == 'download'), None)
        shots = [f for f in imgs if f != map_img]  # 파일명(시간) 순 = 전체-화장실-세부
        info = {}
        p = os.path.join(d, 'info.json')
        if os.path.exists(p):
            try:
                with open(p, encoding='utf-8') as fh:
                    info = json.load(fh)
            except Exception as e:
                info = {'memo': f'info.json 오류: {e}'}
        url = lambda f: f'{quote(name)}/{quote(f)}'
        m = re.search(r'\d+', name)
        houses.append({
            'name': name,
            'price': int(m.group()) if m else None,
            'link': info.get('link'),
            'floor': info.get('floor'),
            'memo': info.get('memo'),
            'shots': [url(f) for f in shots],
            'map': url(map_img) if map_img else None,
        })
    houses.sort(key=lambda h: (h['price'] is None, h['price'], h['name']))
    return houses

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)
    def do_GET(self):
        if self.path.split('?')[0] in ('/api/houses', '/data.json'):
            body = json.dumps(load_houses(), ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

def build():
    with open(os.path.join(ROOT, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(load_houses(), f, ensure_ascii=False, indent=1)

if __name__ == '__main__':
    import sys
    if 'build' in sys.argv:
        build(); raise SystemExit
    print('http://localhost:8000')
    ThreadingHTTPServer(('127.0.0.1', 8000), H).serve_forever()
