# A streamed answer holds the connection open for a while, so a client with a
# timeout can give up in the middle, after the server has already charged the
# card at the start. The client cannot tell a charge-that-then-streamed from a
# request that never arrived, so it retries, and is charged again. The fix is
# chapter seventeen's: one idempotency key across the retries of one charge.
import socket
import threading
import time

HOST, PORT = "127.0.0.1", 8700
ledger = []
applied = set()


def serve(conn):
    data = conn.recv(4096).decode("latin1")
    key = None
    for line in data.split("\r\n"):
        if line.lower().startswith("idempotency-key:"):
            key = line.split(":", 1)[1].strip()
    if key and key in applied:
        try:
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\n"
                         b"already done")
        except OSError:
            pass
        conn.close()
        return
    ledger.append("charged")                 # the charge happens up front
    if key:
        applied.add(key)
    try:
        conn.sendall(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n")
        for word in ("your ", "receipt ", "is ", "on ", "its ", "way "):
            b = word.encode()
            conn.sendall(b"%x\r\n%s\r\n" % (len(b), b))
            time.sleep(0.4)                  # gap wider than the client timeout
        conn.sendall(b"0\r\n\r\n")
    except OSError:
        pass                                 # client hung up mid-stream
    conn.close()


def server(stop):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(8)
    s.settimeout(0.2)
    while not stop.is_set():
        try:
            conn, _ = s.accept()
        except socket.timeout:
            continue
        threading.Thread(target=serve, args=(conn,), daemon=True).start()
    s.close()


def buy(key=None):
    c = socket.create_connection((HOST, PORT))
    req = "GET /buy HTTP/1.1\r\nHost: x\r\n"
    if key:
        req += "Idempotency-Key: %s\r\n" % key
    c.sendall((req + "\r\n").encode())
    c.settimeout(0.25)
    try:
        while c.recv(4096):
            pass
        return "completed"
    except socket.timeout:
        return "gave up mid-stream"
    finally:
        c.close()


def run(label, key):
    ledger.clear()
    applied.clear()
    print(label)
    for attempt in range(1, 3):
        print("  attempt %d: %s" % (attempt, buy(key)))
    print("  ledger: %r  (charged %d time%s)"
          % (ledger, len(ledger), "" if len(ledger) == 1 else "s"))


if __name__ == "__main__":
    stop = threading.Event()
    t = threading.Thread(target=server, args=(stop,))
    t.start()
    time.sleep(0.1)
    run("no idempotency key, so the retry charges again:", None)
    run("one idempotency key across both attempts:", "buy-42")
    stop.set()
    t.join()
