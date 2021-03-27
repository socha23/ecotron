
from tick_aware import TickAware

SPEED_SCALING = 0.5

#DEGREES_PER_LINK = 135.114885 # speed = 0.25

DEGREES_PER_LINK = 136.065 # speed = 0.5

#DEGREES_PER_LINK = 135.2 # 0.,5

class Conveyor(TickAware):
    def __init__(self, motor, links_per_move=5):
        TickAware.__init__(self)
        self._motor = motor
        self._speed = 0
        self._last_wait_start = 0
        self._waiting = True
        self._started = False
        self._links_per_move = links_per_move
        self._wait_time = 2
        self._moves_left = -1

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        if speed < -1 or speed > 1:
            raise f"Speed needs to be between -1 and 1, but {speed} received"
        self._speed = speed

    def _degrees_per_one_move(self):
        return self._links_per_move * DEGREES_PER_LINK

    @property
    def wait_time(self):
        return self._wait_time

    @wait_time.setter
    def wait_time(self, val):
        self._wait_time = val


    def start(self, moves_left = -1):
        self._started = True
        self._moves_left = moves_left

    def stop(self):
        self._started = False
        self._waiting = True
        self._last_wait_start = 0    

    def tick(self, cur_s, delta_s):        
        if self._started and self._waiting and cur_s > self._last_wait_start + self.wait_time and self._moves_left != 0:
            self._waiting = False
            self._motor.start_speed_for_degrees(self.speed * SPEED_SCALING, self._degrees_per_one_move(), on_completed=self.on_move_completed)
            if self._moves_left > 0:
                self._moves_left -= 1
        if self._moves_left == 0:
            self.stop()


    def on_move_completed(self):
        self._waiting = True
        if  self._started:
            self._last_wait_start = self.current_time()
