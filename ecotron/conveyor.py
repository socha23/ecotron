from components.distance_meter import DistanceMeter
from adafruit_mcp3xxx.mcp3008 import P0

from components.toggle import Toggle
from components.button import Button
from components.potentiometer import Potentiometer
from tick_aware import TickAware
from director import Script
from ecotron.widget import Widget
from sound import Clip

# todo no longer conv controls; extract
class ConveyorControls:
    def __init__(self, mcp23017, mcp3008):
        self.toggle = Toggle(mcp23017.get_pin(7))
        self.potentiometer = Potentiometer(mcp3008, P0)
        self.button_blue = Button(mcp23017.get_pin(6))
        self.button_green = Button(mcp23017.get_pin(5))
        self.button_yellow = Button(mcp23017.get_pin(4))
        self.button_red = Button(mcp23017.get_pin(3))


CONVEYOR_SPEED = 0.15
POS_PER_LINK = 140
LINKS_PER_MOVE = 5
PAUSE_DURATION = 5
LINKS_IN_CHAIN = 40
POS_UPDATE_DELTA = 5

PLANT_COUNT = 8

CLIP_CONVEYOR = Clip("./resources/gear_unlock.ogg", volume=1, stereo=[1, 0.5])

class Plant:
    def __init__(self, idx, belt):
        self._idx = idx
        self._belt = belt

    def belt_position(self):
        return (((self._idx + self._belt._moves_done) % PLANT_COUNT) + self._belt.phase()) * LINKS_PER_MOVE


class Belt:
  def __init__(self, motor, analog_value_provider):
    self._motor = motor
    self._motor.set_feedback_mode(POS_UPDATE_DELTA)
    motor.reset_position(0)
    self._moves_done = 0
    self._position_at_move_start = 0
    self._position_at_move_end = 0
    self._distance_meter = DistanceMeter(analog_value_provider)
    self._distance_meter.on_object_passed = self._plant_passed_distance_meter
    self._next_move_correction = 0
    self._on_move_complete = lambda: None

  def _plant_passed_distance_meter(self):
    motor_pos = self._motor.position()
    halfway_point = (self._position_at_move_start + self._position_at_move_end) / 2
    if motor_pos < halfway_point:
      # we're late. We need to correct by moving more.
      self._next_move_correction = motor_pos - self._position_at_move_start
    else:
      # we're early. We need to correct by moving less.
      self._next_move_correction = motor_pos - self._position_at_move_end

  def on_move_done(self):
      self._moves_done += 1
      self._on_move_complete()
      self._on_move_complete = lambda: None
      self._position_at_move_start = self._position_at_move_end

  def move(self, links_count, on_complete=lambda: None):
        if self._motor.is_busy():
            on_complete()
            return
        self._on_move_complete = on_complete
        self._position_at_move_end = self._position_at_move_start + links_count * POS_PER_LINK + self._next_move_correction
        self._next_move_correction = 0
        self._motor.goto_absolute_position(self._position_at_move_end, CONVEYOR_SPEED, on_complete=self.on_move_done)

  def phase(self):
    if self._position_at_move_start == self._position_at_move_end:
      return 0
    return (self._motor.position() - self._position_at_move_start) / (self._position_at_move_end - self._position_at_move_start)

class Conveyor(Widget):

    def __init__(self, motor, analog_value_provider, director):
      Widget.__init__(self)
      self._director = director
      self._belt = Belt(motor, analog_value_provider)
      self.plants = [Plant(idx, self._belt) for idx in range(PLANT_COUNT)]
      self.on_move_complete_listeners = []
      self._phase_listeners = []

    def _notify_on_move_complete_listeners(self):
      for listener in self.on_move_complete_listeners:
        listener()

    def add_phase_listener(self, phase, handler):
        self._phase_listeners.append(PhaseListener(phase, handler, self))

    def move_and_wait(self, callback=lambda:None):
      (Script()
        .add_step(CLIP_CONVEYOR.play)
        .add_sleep(0.3)
        .add_async_step(lambda c: self._belt.move(LINKS_PER_MOVE, c))
        .add_step(self._notify_on_move_complete_listeners)
        .add_sleep(PAUSE_DURATION)
        .add_step(self.idle)
      ).execute()

    def idle(self):
      if self.on:
        self.move_and_wait()

    def when_turn_on(self):
      self.move_and_wait()

    def phase(self):
      return self._belt.phase()


class PhaseListener(TickAware):
    def __init__(self, phase, handler, conveyor):
        TickAware.__init__(self)
        self._phase = phase
        self._handler = handler
        self._conveyor = conveyor
        self._last_phase = conveyor.phase()

    def tick(self, t, d):
        current_phase = self._conveyor.phase()
        if current_phase != self._last_phase:
            if ((
                self._last_phase < self._phase and self._phase <= current_phase)
                or (self._last_phase < self._phase and current_phase < self._last_phase) # rollover
            ):
                self._handler()
            self._last_phase = current_phase


