import threading
import time

TICK_AWARES = []
DEFAULT_TICK_TIME = 0.01


class TickAwareController:
    def __init__(self, initial_time = time.time(), tick_time = DEFAULT_TICK_TIME):
        self._tick_awares = []
        self._time = initial_time
        self._tick_time = tick_time
        self.on = False        
        threading.Thread(target=self.tick_thread, daemon=True, name="tick thread").start()

    def tick_thread(self):
        while True:
            if self.on:
                cur_time = time.time()
                if cur_time > self._time:
                    self.tick(cur_time)
            time.sleep(self._tick_time)

    def tick(self, cur_s):
        delta = cur_s - self._time
        for a in self._tick_awares:
            a.tick(cur_s, delta)
        self._time = cur_s


    def current_time(self):
        return self._time

    def register_tick_aware(self, tick_aware):
        self._tick_awares.append(tick_aware)

    def unregister_tick_aware(self, tick_aware):
        self._tick_awares.remove(tick_aware)


DEFAULT_CONTROLLER = TickAwareController()

class TickAware:
    def __init__(self, controller=DEFAULT_CONTROLLER):
        self._tick_aware_controller = controller
        self._tick_aware_controller.register_tick_aware(self)

    def tick(self, cur_s, delta_s):
        pass

    def current_time(self):
        return self._tick_aware_controller.current_time()

    def close(self):
        self._tick_aware_controller.unregister_tick_aware(self)
