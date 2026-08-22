"""Two locks, two threads, opposite orders, and a program that never ends.

The chapter says a deadlock happens when one thread holds lock A and wants
B while another holds B and wants A. This makes exactly that, watches it
hang, and then fixes it the one way that always works: make every thread
take the locks in the same order.

Run it with:  python3 deadlock.py
"""

import threading
import time


def grab(name, a, b):
    with a:
        time.sleep(0.1)         # give the other thread time to grab its first
        with b:
            print(f"    {name} got both")


def run(label, swap_second_thread):
    a = threading.Lock()
    b = threading.Lock()
    order_one = (a, b)
    order_two = (b, a) if swap_second_thread else (a, b)
    one = threading.Thread(target=grab, args=("left ", *order_one),
                           daemon=True)
    two = threading.Thread(target=grab, args=("right", *order_two),
                           daemon=True)
    print(label)
    one.start()
    two.start()
    one.join(timeout=2.0)
    two.join(timeout=2.0)
    if one.is_alive() or two.is_alive():
        print("    still stuck after 2s: this is the deadlock")
    print()


run("opposite orders:", swap_second_thread=True)
run("same order:", swap_second_thread=False)
