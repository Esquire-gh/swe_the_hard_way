"""Where your route functions actually run under uvicorn.

Nothing in the guestbook mentions threads, yet chapter thirteen said two
visitors at once need somewhere to run at once. This shows where: an
ordinary def route reports the thread it is running on, and an async def
route reports that it is on the event loop itself. Hit the def route a few
times at once and the thread names differ, because uvicorn hands each
plain function to a thread from a pool so a slow one cannot stop the loop.

Install: pip install -r requirements.txt
Run it:  uvicorn thread_names:app --port 8000
Then:    curl -s http://127.0.0.1:8000/sync   (a few times, at once)
         curl -s http://127.0.0.1:8000/async
"""

import threading
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/sync")
def on_a_thread():
    time.sleep(0.3)                       # stand in for slow work
    here = threading.current_thread()
    return {"kind": "def", "thread": here.name, "id": here.ident}


@app.get("/async")
async def on_the_loop():
    here = threading.current_thread()
    return {"kind": "async def", "thread": here.name, "id": here.ident}
