#!/usr/bin/env python3
"""NEON SPIN dev server: serves the game on :8420 and records progress
telemetry the game POSTs to /log, so balance/pacing can be inspected.

Run:  python3 devserver.py
Log:  progress.log  (gitignored)
"""
import http.server, socketserver, json, datetime, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
ROOT = os.path.dirname(os.path.abspath(__file__))
LOG  = os.path.join(ROOT, "progress.log")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/log":
            n = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(n).decode("utf-8", "ignore")
            try:
                d = json.loads(raw)
            except Exception:
                d = {"raw": raw}
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            line = ("{ts} | {t:>5}s | {reason:<6} | spins {spins:<6} "
                    "| coins {coinsF:<8} | earned {earnedF:<8} | cps {cpsF:<8}/s "
                    "| x{mult:<10} | luck {luck}% | reels {reels} | chips {chips} "
                    "| prest {prestiges} | best {bestWin}").format(
                ts=ts, t=d.get("t", "?"), reason=d.get("reason", "?"),
                spins=d.get("spins", "?"), coinsF=d.get("coinsF", "?"),
                earnedF=d.get("earnedF", "?"), cpsF=d.get("cpsF", "?"),
                mult=d.get("mult", "?"), luck=d.get("luck", "?"),
                reels=d.get("reels", "?"), chips=d.get("chips", "?"),
                prestiges=d.get("prestiges", "?"), bestWin=d.get("bestWin", "?"))
            with open(LOG, "a") as f:
                f.write(line + "\n")
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass  # silence per-request noise

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    os.chdir(ROOT)
    print("NEON SPIN dev server -> http://localhost:%d/  (logging to %s)" % (PORT, LOG))
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()
