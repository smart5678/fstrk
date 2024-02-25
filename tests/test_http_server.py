import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from django.conf import settings


class TestHTTPServer(HTTPServer):
    def run(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()


class HandleRequests(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        """Reads post request body"""
        self._set_headers()
        content_len = int(self.headers['content-length'])
        post_body = self.rfile.read(content_len)
        self.wfile.write(str.encode('received post request:<br>{}'.format(post_body)))

    def log_request(self, code='-', size='-'):
        pass


@pytest.fixture()
def test_http_server():
    url = settings.RECEIVER_URL
    host, port = url.split('/')[2].split(':')
    # serve_Run forever under thread
    server = TestHTTPServer((host, int(port)), HandleRequests)
    thread = threading.Thread(None, server.run)
    thread.start()
    yield url
    server.shutdown()
    thread.join()
