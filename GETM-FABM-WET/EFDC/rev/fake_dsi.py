# -*- coding: utf-8 -*-
"""Minimal, robust DSI licensing stub: always answers 200 + JSON, one request per connection.

python -X utf8 rev/fake_dsi.py [port]
"""
import json
import os
import socket
import sys
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "fake_dsi_requests.txt")
RESP = os.path.join(BASE, "demo_resp.txt")
PKGS = os.path.join(BASE, "demo_resp_packages.txt")


def log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def read(path, fallback):
    try:
        t = open(path, "r", encoding="utf-8-sig").read().strip()
        return t or fallback
    except Exception:
        return fallback


def body_for(path):
    if "GetTimeLocation" in path:
        return time.strftime("%H:%M:%S")
    if "getupgradepackages" in path:
        return read(PKGS, '{"Status":"Success","ReturnedData":[]}')
    return read(RESP, '{"Status":"Success","ReturnedData":"<XmlResult><error>0</error></Status>","Exception":""}')


def handle(conn):
    try:
        conn.settimeout(20)
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(65536)
            if not chunk:
                return
            data += chunk
        head, rest = data.split(b"\r\n\r\n", 1)
        lines = head.decode("latin1").split("\r\n")
        method, path, _ = (lines[0].split(" ") + ["", "", ""])[:3]
        length = 0
        for h in lines[1:]:
            if h.lower().startswith("content-length:"):
                length = int(h.split(":")[1].strip())
        while len(rest) < length:
            chunk = conn.recv(65536)
            if not chunk:
                break
            rest += chunk
        log("=== %s %s" % (method, path))
        if rest:
            log("   BODY: %r" % (rest[:400],))
        payload = body_for(path).encode("utf-8")
        resp = (b"HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\n"
                b"Content-Length: " + str(len(payload)).encode() + b"\r\nConnection: close\r\n\r\n" + payload)
        conn.sendall(resp)
        log("   -> 200 (%d bytes)" % len(payload))
    except Exception as e:
        log("   !! %s" % e)
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    open(LOG, "w", encoding="utf-8").close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(64)
    log("listening on %d" % port)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
