import http.server
import json
import socketserver
import sys
import threading
import time

LOG = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\fakedemo_requests.txt"


def log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _handle(self, method):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except Exception:
            length = 0
        body = self.rfile.read(length) if length else b""
        log("=== %s %s" % (method, self.path))
        for k, v in self.headers.items():
            log("   H %s: %s" % (k, v))
        if body:
            log("   BODY(%d): %r" % (len(body), body[:800]))

        resp_file = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\demo_resp.txt"
        try:
            body = open(resp_file, "r", encoding="utf-8-sig").read()
        except Exception:
            body = '{"status":"success"}'
        payload = body.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    open(LOG, "w", encoding="utf-8").close()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), H)
    srv.allow_reuse_address = True
    log("listening on %d" % port)
    srv.serve_forever()


