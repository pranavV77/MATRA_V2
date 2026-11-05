"""Loopback-only offline demo: python -m src.review_demo.server --port 8765."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
from urllib.parse import urlsplit

from src.review_demo.service import DemoService
from src.similarity_validation import PROJECT_ROOT

STATIC = Path(__file__).parent / 'static'
LOGGER = logging.getLogger(__name__)


def make_server(port=8765, service=None):
    service = service or DemoService()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args): LOGGER.info(fmt, *args)

        def send_json(self, value, status=200):
            data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers(); self.wfile.write(data)

        def origin_allowed(self):
            allowed_hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            host = self.headers.get('Host','')
            origin = self.headers.get('Origin')
            return host in allowed_hosts and (origin is None or origin in {'http://'+h for h in allowed_hosts})

        def do_GET(self):
            if not self.origin_allowed(): return self.send_json({'error':'Local origin required'},403)
            route = urlsplit(self.path).path
            if route == '/api/health': return self.send_json({'ok':True,'version':'review-0.1'})
            if route == '/api/status': return self.send_json(service.status())
            if route == '/api/evaluation': return self.send_json(service.evaluation())
            files = {'/':('index.html','text/html'), '/app.js':('app.js','text/javascript'), '/style.css':('style.css','text/css')}
            if route not in files: return self.send_json({'error':'Not found'},404)
            filename, mime = files[route]
            data = (STATIC / filename).read_bytes()
            self.send_response(200); self.send_header('Content-Type',mime+'; charset=utf-8')
            self.send_header('Content-Length',str(len(data))); self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers(); self.wfile.write(data)

        def do_POST(self):
            # Consume bounded request bodies before replying: unread bytes can
            # otherwise reset the connection on Windows and hide JSON errors.
            try: incoming_size = int(self.headers.get('Content-Length','0'))
            except ValueError: incoming_size = 0
            body = self.rfile.read(incoming_size) if 0 < incoming_size <= 65536 else b''
            if not self.origin_allowed(): return self.send_json({'error':'Local origin required'},403)
            route = urlsplit(self.path).path
            if route not in ('/api/recommend','/api/export'): return self.send_json({'error':'Not found'},404)
            if self.headers.get_content_type() != 'application/json': return self.send_json({'error':'JSON body required'},415)
            try: size = int(self.headers.get('Content-Length','0'))
            except ValueError: return self.send_json({'error':'Invalid content length'},400)
            if size <= 0 or size > 16384: return self.send_json({'error':'Request body must be 1..16384 bytes'},413)
            try:
                payload = json.loads(body.decode('utf-8'))
                result = service.recommend(payload) if route == '/api/recommend' else service.export(payload)
                return self.send_json(result)
            except (ValueError, TypeError, UnicodeError) as exc:
                return self.send_json({'error':str(exc)},400)
            except Exception:
                LOGGER.exception('Review-demo request failed')
                return self.send_json({'error':'Request could not be completed; see the local server log'},500)

    return ThreadingHTTPServer(('127.0.0.1',port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535: parser.error('Port must be 0..65535')
    directory = PROJECT_ROOT / 'logs/review_demo'; directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=directory/'server.log',level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    server = make_server(args.port)
    print(f'MATRA review demo: http://127.0.0.1:{server.server_port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__': main()
