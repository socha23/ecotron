import threading
import time

TICK_AWARES = []
DEFAULT_TICK_TIME = 0

import logging

logger = logging.getLogger(__name__)

class TickAwareController:
    def __init__(self, initial_time = time.time(), tick_time = 0, debug=False):
        self._tick_awares = []
        self._time = initial_time
        self._tick_time = tick_time
        self.on = False
        self._debug = debug
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
            if self._debug:
                a.tick_with_logging(cur_s, delta)
            else:
                a.tick(cur_s, delta)
        if self._debug:
            logger.info(f"TickAware loop took {time.time() - cur_s}")
        self._time = cur_s


    def current_time(self):
        return self._time

    def register_tick_aware(self, tick_aware):
        self._tick_awares.append(tick_aware)

    def unregister_tick_aware(self, tick_aware):
        self._tick_awares.remove(tick_aware)


DEFAULT_CONTROLLER = TickAwareController(DEFAULT_TICK_TIME)

class TimeAware:
    def __init__(self, controller=DEFAULT_CONTROLLER):
        self._tick_aware_controller = controller

    def current_time(self):
        return self._tick_aware_controller.current_time()


class SpentTimeCalculator:
    def __init__(self, tick_aware, log_every=100):
        self._tick_aware = tick_aware
        self._count = 0
        self._cumulative_time = 0
        self._last_tick_enter = 0
        self._log_every = log_every

    def tick_enter(self):
        self._last_tick_enter = time.time()

    def tick_leave(self):
        self._count += 1
        self._cumulative_time += (time.time() - self._last_tick_enter)
        if self._count % self._log_every == 0:
            logger.info(f"{self._tick_aware} stats after {self._count} runs: {self._cumulative_time / self._count:.4f} s per tick")


class TickAware:
    def __init__(self, controller=DEFAULT_CONTROLLER):
        self._tick_aware_controller = controller
        self._tick_aware_controller.register_tick_aware(self)
        self._spent_time_calculator = SpentTimeCalculator(self)

    def tick(self, cur_s, delta_s):
        pass

    def tick_with_logging(self, cur_s, delta_s):
        self._spent_time_calculator.tick_enter()
        self.tick(cur_s, delta_s)
        self._spent_time_calculator.tick_leave()

    def current_time(self):
        return self._tick_aware_controller.current_time()

    def close(self):
        self._tick_aware_controller.unregister_tick_aware(self)
