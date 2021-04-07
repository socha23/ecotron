from components.button import Button
from components.potentiometer import Potentiometer
from adafruit_mcp3xxx.mcp3008 import P0
from tick_aware import TickAware
from director import Director, Script


class ConveyorControls:
    def __init__(self, mcp23017, mcp3008):
        self.master_switch = Button(mcp23017.get_pin(7))
        self.potentiometer = Potentiometer(mcp3008, P0)
        self.button_blue = Button(mcp23017.get_pin(6))
        self.button_green = Button(mcp23017.get_pin(5))
        self.button_yellow = Button(mcp23017.get_pin(4))
        self.button_red = Button(mcp23017.get_pin(3))

STATE_WAITING = 0
STATE_RUNNING = 1

POS_PER_LINK = 136

SPEED_SCALING = 0.5


class Conveyor(TickAware):
    def __init__(self, motor, controls, director, links_per_move=5):
        TickAware.__init__(self)
        self._director = director
        self._motor = motor
        motor.reset_position(0)
        self._current_position = motor.position()
        self._links_per_move = links_per_move
        self._state = STATE_WAITING
        self._controls = controls

    def tick(self, cur_s, delta_s):        
        if self._state == STATE_RUNNING or not self._is_on() or abs(self._speed()) < 0.05 :
            return        
        self._director.execute(Script()
        .add_step(self.init_execution)
        .add_async_step(lambda callback: self.move_conveyor(callback))
        .add_sleep(1)
        .add_step(self.end_execution)
        )

    def init_execution(self):
        self._state = STATE_RUNNING

    def move_conveyor(self, on_complete):
        dest_position = self._current_position + self._direction() * self._links_per_move * POS_PER_LINK
        self._motor.goto_absolute_position(dest_position, abs(self._speed()), on_complete=on_complete)
        self._current_position = dest_position

    def end_execution(self):
        self._state = STATE_WAITING

    def _is_on(self):
        return self._controls.master_switch.is_pressed()

    def _direction(self):
        return 1 if self._speed() > 0 else -1

    def _speed(self):
        return (self._controls.potentiometer.value - 0.5) * 2 * SPEED_SCALING
