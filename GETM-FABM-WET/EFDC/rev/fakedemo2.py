import http.server
import json
import os
import socketserver
import sys

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"
LOG = os.path.join(BASE, "fakedemo_requests.txt")
DEFAULT_FILE = os.path.join(BASE, "demo_resp.txt")
PACKAGES_FILE = os.path.join(BASE, "demo_resp_packages.txt")


def log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def read(path, fallback):
    try:
        return open(path, "r", encoding="utf-8-sig").read().strip()
    except Exception:
        return fallback


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _handle(self, method):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except Exception:
            length = 0
        body = self.rfile.read(length) if length else b""
        log("=== %s %s  (UA=%s, CT=%s)" % (method, self.path,
                                            self.headers.get("User-Agent", "-"),
                                            self.headers.get("Content-Type", "-")))
        if body:
            log("   BODY(%d): %r" % (len(body), body[:600]))

        if "GetTimeLocation" in self.path:
            body_text = __import__("datetime").datetime.now().strftime("%H:%M:%S")
        elif "getupgradepackages" in self.path:
            body_text = read(PACKAGES_FILE, '{"Status":"Success","ReturnedData":[]}')
        else:
            body_text = read(DEFAULT_FILE, '{"Status":"Success","ReturnedData":"<status>ok</status>","Exception":""}')

        payload = body_text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def setup(self):
        log('-- connection from %s' % (self.client_address,))
        http.server.BaseHTTPRequestHandler.setup(self)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_HEAD(self):
        self._handle("HEAD")

    def do_PUT(self):
        self._handle("PUT")

    def do_OPTIONS(self):
        self._handle("OPTIONS")

    def do_DELETE(self):
        self._handle("DELETE")

    def log_request(self, code='-', size='-'):
        log("   -> %s" % (code,))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    open(LOG, "w", encoding="utf-8").close()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), H)
    srv.allow_reuse_address = True
    log("listening on %d" % port)
    srv.serve_forever()



