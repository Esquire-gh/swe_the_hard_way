# An agent is a client. It asks a model server what to do, reads the answer,
# and acts on it by calling another server, with the same retries and
# idempotency keys a careful client has used since chapter five. Nothing in
# this file is new: it is chapters five through seventeen, arranged as a loop.
#
# The two servers it talks to are stubbed in-process so the file runs alone.
import http.server
import json
import socket
import threading
import time
import urllib.error
import urllib.request

signed = []                 # the guestbook's rows
applied = set()             # idempotency keys the guestbook has honoured
lock = threading.Lock()


class Stub(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/model":
            # the "model": given a question, decides on an action
            name = body["question"].split()[-1].strip("?.")
            self._json({"tool": "sign_guestbook", "name": name})
        elif self.path == "/guestbook":
            key = self.headers.get("Idempotency-Key")
            with lock:
                if key in applied:
                    self._json({"status": "already signed"})
                    return
                applied.add(key)            # reserve now so a retry is caught
            time.sleep(0.5)              # slow work, trips the timeout
            signed.append(body["name"])
            self._json({"status": "signed"})

    def _json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def post(path, obj, key=None, timeout=10):
    req = urllib.request.Request(
        "http://127.0.0.1:8600" + path,
        data=json.dumps(obj).encode(),
        headers={"Content-Type": "application/json"},
    )
    if key:
        req.add_header("Idempotency-Key", key)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def agent(question):
    print("agent asks the model:", question)
    plan = post("/model", {"question": question})
    name = plan["name"]
    print("  model says: call %s for %r" % (plan["tool"], name))
    key = "sign-" + name                 # one key for every retry of this run
    for attempt in range(1, 4):
        try:
            out = post("/guestbook", {"name": name}, key=key, timeout=0.2)
            print("  attempt %d: %s" % (attempt, out["status"]))
            return
        except (urllib.error.URLError, TimeoutError, socket.timeout):
            print("  attempt %d timed out, retrying same key" % attempt)
            time.sleep(0.25)


if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8600), Stub)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    agent("please sign the guestbook for Ada")
    time.sleep(0.6)                       # let the slow first attempt finish
    print("guestbook rows:", signed)
    srv.shutdown()
