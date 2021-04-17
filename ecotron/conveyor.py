from adafruit_mcp3xxx.mcp3008 import P0

from components.button import Button
from components.potentiometer import Potentiometer
from tick_aware import TickAware
from director import Director, Script
from speech import say, SpeechLines
from ecotron.widget import Widget

class ConveyorControls:
    def __init__(self, mcp23017, mcp3008):
        self.master_switch = Button(mcp23017.get_pin(7))
        self.potentiometer = Potentiometer(mcp3008, P0)
        self.button_blue = Button(mcp23017.get_pin(6))
        self.button_green = Button(mcp23017.get_pin(5))
        self.button_yellow = Button(mcp23017.get_pin(4))
        self.button_red = Button(mcp23017.get_pin(3))


RESET_POS_ON_FINISH_CALIBRATION = True

class Conveyor(TickAware, Widget):

    # positive speed = CCW movement
    # calibrated to positive speed, with 0 = cooker

    # POS_PER_LINK = 131.5
    # 132 too much
    # smething started to suck, temp override
    POS_PER_LINK = 133

    LINKS_IN_CHAIN = 40

    STATE_WAITING = 0
    STATE_STEPPING = 1

    def __init__(self, motor, controls, director):
        TickAware.__init__(self)
        Widget.__init__(self)
        self._director = director
        self._motor = motor
        motor.reset_position(0)
        self._current_position = 0
        self._state = Conveyor.STATE_WAITING
        self._controls = controls        
        self._last_move_start_pos = None

    def move_links(self, links, speed=0.5, callback=lambda:None):
        if not speed:
            return
        self.init_move()
        self._director.execute(Script()
            .add_async_step(lambda c: self.move_conveyor(self._direction() * links * Conveyor.POS_PER_LINK, speed, c))
            .add_step(self.end_move)
            .add_step(callback)
        )

    def init_move(self):
        self._state = Conveyor.STATE_STEPPING

    def move_conveyor(self, how_much, speed=0.5, on_complete=lambda:None):
        if self._motor.is_busy():
            on_complete()
            return
        self._last_move_start_pos = self._current_position
        dest_position = self._current_position + how_much
        self._motor.goto_absolute_position(dest_position, speed * 0.3, on_complete=on_complete)
        self._current_position = dest_position

    def end_move(self):
        self._state = Conveyor.STATE_WAITING
        self._last_move_start_pos = None

    def is_moving(self):
        return self._state == Conveyor.STATE_STEPPING

    def phase(self):
        if self._last_move_start_pos == None:
            return 0
        return min(1, (self._motor.position() - self._last_move_start_pos) / (self._current_position - self._last_move_start_pos))

    def _direction(self):
        return 1 if self._speed() > 0 else -1

    def _speed(self):
        pot = self._controls.potentiometer.value
        if pot < 0.1:
            return 0
        else:
            return pot
    
    def reset_position(self):
        self._motor.reset_position()
        self._current_position = 0

    CALIBRATION_STEP = int(POS_PER_LINK /4)
    CALIBRATION_SPEED = 0.3

    def calibration_forward(self, on_complete=lambda:None):
        self.move_conveyor(Conveyor.CALIBRATION_STEP, Conveyor.CALIBRATION_SPEED, on_complete)

    def calibration_backward(self, on_complete=lambda:None):
        self.move_conveyor(-Conveyor.CALIBRATION_STEP, Conveyor.CALIBRATION_SPEED, on_complete)

