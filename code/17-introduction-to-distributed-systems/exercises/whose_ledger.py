"""Move the delay, and watch the client's belief and the server's truth split.

no_answer.py sleeps before doing the work, so a timeout might mean nothing
happened. Move the sleep to between the charge and the reply and a timeout
means the charge did happen and the client will never know it. This runs
both orderings, prints what the client believes and what the server's
ledger records, and the gap between them is the whole lesson: across
machines the server's ledger is the truth, and the client's belief is a
guess made from a timeout.

Run it with:  python3 whose_ledger.py
"""

import socket
import threading
import time


def run(order, port):
    ledger = []

    def server():
        listening = socket.socket()
        listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listening.bind(("127.0.0.1", port))
        listening.listen(8)
        connection, _ = listening.accept()
        connection.recv(4096)
        if order == "sleep first":
            time.sleep(1.0)                  # slow, then maybe charge
        ledger.append("charged")
        if order == "charge first":
            time.sleep(1.0)                  # charge, then slow reply
        try:
            connection.sendall(b"HTTP/1.1 200 OK\r\n"
                               b"Content-Length: 3\r\n\r\nok\n")
        except OSError:
            pass
        connection.close()
        listening.close()

    thread = threading.Thread(target=server, daemon=True)
    thread.start()
    time.sleep(0.3)

    client = socket.socket()
    client.settimeout(0.5)
    client.connect(("127.0.0.1", port))
    client.sendall(b"POST /charge HTTP/1.1\r\nHost: x\r\n\r\n")
    try:
        client.recv(4096)
        belief = "charged"
    except socket.timeout:
        belief = "no idea"
    client.close()
    time.sleep(1.2)
    print(f"{order:14} client believes: {belief:9} server ledger: {ledger}")


run("sleep first", 8332)
run("charge first", 8333)
print("\nboth clients timed out and believe 'no idea';")
print("the server's ledger is the only record of what truly happened")
