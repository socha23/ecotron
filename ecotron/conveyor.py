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

    POS_PER_LINK = 131.5
    # 132 too much
    LINKS_IN_CHAIN = 40

    STATE_WAITING = 0
    STATE_STEPPING = 1
    STATE_CALIBRATION = 2

    def __init__(self, motor, controls, director, links_per_plant=5):
        TickAware.__init__(self)
        Widget.__init__(self)
        self._director = director
        self._motor = motor
        motor.reset_position(0)
        self._current_position = 0
        self._links_per_plant = links_per_plant
        self._state = Conveyor.STATE_WAITING
        self._controls = controls
        self.on_plants_moved = lambda phase, positions: None
        motor.on_position_changed = self._on_conveyor_moved
        self._last_move_start = None
        self._last_pause_start = None
        self._last_move_duration = None

    def pause_duration(self):
        return 3 + 7 * (1 - abs(self._speed())) 

    def _on_conveyor_moved(self, _):
        if self.on_plants_moved != None:
            self.on_plants_moved(self.phase(), self.plant_positions())

    def is_calibrating(self):
        return self._state == Conveyor.STATE_CALIBRATION

    def tick(self, cur_s, delta_s):        
        if not self.on:
            return
        if self._state != Conveyor.STATE_WAITING or not self._is_on() or abs(self._speed()) < 0.05 :
            return        
        self.move_one_step()

    def move_links(self, links, callback=lambda:None):
        self.init_move()
        self._director.execute(Script()
            .add_async_step(lambda c: self.move_conveyor(self._direction() * links * Conveyor.POS_PER_LINK, c))
            .add_step(self.end_move)
            .add_sleep(self.pause_duration())
            .add_step(self.end_phase)
            .add_step(callback)
        )

    def move_one_step(self, callback=lambda:None):
        self.move_links(self._links_per_plant, callback)

    def plant_positions(self):
        plant_count = int(Conveyor.LINKS_IN_CHAIN / self._links_per_plant)
        return [(idx + self.phase()) * self._links_per_plant for idx in range(plant_count)]
        

    def init_move(self):
        self._state = Conveyor.STATE_STEPPING
        self._last_move_start = self.current_time()
        self._last_pause_start = None

    def move_conveyor(self, how_much, on_complete=lambda:None):
        if self._motor.is_busy():
            on_complete()
            return
        dest_position = self._current_position + how_much
        self._motor.goto_absolute_position(dest_position, abs(self._motor_speed()), on_complete=on_complete)
        self._current_position = dest_position

    def end_move(self):
        self._last_move_duration = self.current_time() - self._last_move_start
        self._last_move_start = None
        self._last_pause_start = self.current_time()
        if self.on_plants_moved != None:
            self.on_plants_moved(0, self.plant_positions())

    def duration_since_move_start(self):
        if self._last_move_start:
            return self.current_time() - self._last_move_start
        else:
            return None

    def is_moving(self):
        return self._state == Conveyor.STATE_STEPPING

    def prognosed_time_to_finish_pause(self):
        if self._last_pause_start:
            return max(0, self._last_pause_start + self.pause_duration() - self.current_time())
        else:
            return None


    def prognosed_time_to_finish_move(self):
        if self._last_move_duration and self.duration_since_move_start():
            return self._last_move_duration - self.duration_since_move_start()

    def end_phase(self):
        if self._state == Conveyor.STATE_STEPPING:
            self._state = Conveyor.STATE_WAITING

    def phase(self):
        return (self._motor.position() % (self._links_per_plant * Conveyor.POS_PER_LINK)) / (self._links_per_plant * Conveyor.POS_PER_LINK)


    def _is_on(self):
        return self._controls.master_switch.is_pressed()

    def _direction(self):
        return 1 if self._speed() > 0 else -1

    def _speed(self):
        pot = (self._controls.potentiometer.value - 0.5) * 2
        if abs(pot) < 0.1:
            return 0
        else:
            return pot
    
    def _motor_speed(self):
        s = self._speed()
        sign = 1 if s > 0 else -1
        if abs(s) < 0.1:
            return 0
        else:
            return sign * (0.1 + ((abs(s) - 0.1) * 0.15))


    #####################################
    # Calibration
    #####################################

    CALIBRATION_STEP = int(POS_PER_LINK /4)

    def enter_calibration(self):
        self._state = Conveyor.STATE_CALIBRATION
        say(SpeechLines.CONVEYOR_CALIBRATION_STARTED)

    def finish_calibration(self):
        if RESET_POS_ON_FINISH_CALIBRATION:
            self._motor.reset_position()
            self._current_position = 0
        say(SpeechLines.CONVEYOR_CALIBRATION_COMPLETE)
        self._state = Conveyor.STATE_WAITING

    def calibration_forward(self, on_complete=lambda:None):
        self.move_conveyor(Conveyor.CALIBRATION_STEP, on_complete)

    def calibration_backward(self, on_complete=lambda:None):
        self.move_conveyor(-Conveyor.CALIBRATION_STEP, on_complete)

