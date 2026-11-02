# -*- coding: utf-8 -*-
"""Minimal offline license stub (proven variant): every call gets HTTP 200 + simple JSON."""
import http.server, socketserver, sys, time, os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "fakedemo.log")

def log(s):
    try:
        open(LOG, "a", encoding="utf-8").write("%s %s\n" % (time.strftime("%H:%M:%S"), s))
    except Exception:
        pass

class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def _h(self, m):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except Exception:
            n = 0
        if n:
            self.rfile.read(n)
        log("%s %s" % (m, self.path))
        if "GetTimeLocation" in self.path:
            body = time.strftime("%H:%M:%S")
        elif "getupgradepackages" in self.path:
            body = '{"Status":"Success","ReturnedData":[]}'
        else:
            body = '{"Status":"Success","ReturnedData":"<status>ok</status>","Exception":""}'
        p = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(p)))
        self.end_headers()
        self.wfile.write(p)
    def do_GET(self): self._h("GET")
    def do_POST(self): self._h("POST")
    def do_HEAD(self): self._h("HEAD")
    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), H)
    log("listening on %d" % port)
    print("license stub listening on 127.0.0.1:%d" % port, flush=True)
    srv.serve_forever()
