from tick_aware import TickAware

SPEED_SCALING = 0.5

DEGREES_PER_LINK = 135

class Conveyor(TickAware):
    def __init__(self, motor, links_per_move=5):
        TickAware.__init__(self)
        self._motor = motor
        self._speed = 0
        self._last_wait_start = 0
        self._waiting = True
        self._started = False
        self._links_per_move = links_per_move
        self._dest_pos_degrees = 0
        self._cur_pos_degrees = 0

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

    def wait_time(self):
        return 2

    def start(self):
        self._started = True

    def stop(self):
        self._started = False
        self._waiting = True
        self._last_wait_start = 0    

    def tick(self, cur_s, delta_s):        
        if self._started and self._waiting and cur_s > self._last_wait_start + self.wait_time():
            self._waiting = False
            self._dest_pos_degrees += self._degrees_per_one_move()
            degrees_to_move = int(self._dest_pos_degrees - self._cur_pos_degrees)
            self._cur_pos_degrees += degrees_to_move
            self._motor.start_speed_for_degrees(self.speed * SPEED_SCALING, degrees_to_move, on_completed=self.on_move_completed)

    def on_move_completed(self):
        self._waiting = True
        if  self._started:
            self._last_wait_start = self.current_time()
