import threading
import time

TICK_AWARES = []
TICK_TIME = 0.001

last_time = time.time()

def tick():
    global last_time
    while True:
        cur_time = time.time()
        if cur_time > last_time:
            for a in TICK_AWARES:
                a.tick(cur_time, cur_time - last_time)
            last_time = cur_time
        time.sleep(TICK_TIME)


TICK_THREAD = threading.Thread(target=tick, daemon=True, name="TICK_THREAD")
TICK_THREAD.start()

class TickAware:
    def __init__(self):
        TICK_AWARES.append(self)

    def tick(self, cur_s, delta_s):
        pass

    def current_time(self):
        return time.time()
