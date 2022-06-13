from director import DEFAULT_DIRECTOR, Script
from effects.explosion import ExplosionSource, explosion_now
from .properties import DEFAULT_ECOTRON_PROPERTIES
from .lights import Lights
from value_source import AlwaysOff, Sine, repeated_pulse
from .widget import Widget
from sound import Clip
import traceback

OPEN_SPEED = 0.05
CLOSE_SPEED = 0.05

OPEN_ANGLE = 30
CLOSED_ANGLE = 140

CLIP_DOOR = Clip("./resources/hangar_door.ogg", stereo=[0.5, 1])

class ReactorDoor(Widget):
    def __init__(self, door_servo):
        Widget.__init__(self)
        self._door_servo = door_servo

    def when_initialize(self, prop_value):
        if prop_value:
            self._door_servo.move_to(OPEN_ANGLE, 0.5)
        else:
            self._door_servo.move_to(CLOSED_ANGLE, 0.5)

    def when_turn_on(self):
        self.open()

    def when_turn_off(self):
        self.close()

    def open(self):
        s = Script()
        s.add_step(lambda: CLIP_DOOR.play(fadein=0.5))
        s.add_sleep(2.5)
        s.add_step(lambda: self._door_servo.move_to(OPEN_ANGLE, OPEN_SPEED))
        s.add_sleep(6)
        s.add_step(lambda: CLIP_DOOR.fadeout(2))
        s.execute()

    def close(self):
        s = Script()
        s.add_step(lambda: CLIP_DOOR.play(fadein=0.5))
        s.add_sleep(2.5)
        s.add_step(lambda: self._door_servo.move_to(CLOSED_ANGLE, CLOSE_SPEED))
        s.add_sleep(6)
        s.add_step(lambda: CLIP_DOOR.fadeout(2))
        s.execute()


class ReactorWarningLights(Widget):
    def __init__(self, led_1, led_2):
        Widget.__init__(self)
        self._led_1 = led_1
        self._led_2 = led_2

    def when_turn_on(self):
        self._led_1.source = Sine(1.2)
        self._led_2.source = Sine(0.95)

    def when_turn_off(self):
        self._led_1.source = AlwaysOff()
        self._led_2.source = AlwaysOff()

class Reactor:
    def __init__(self, neopixels):
        self._pixels = neopixels
        self._running = False


    def boom(self):
        def _finish_run(self):
            self._running = False

        if self._running:
            return
        self._running = True
        self._boom_script().add_step(lambda: _finish_run(self)).execute()


    def _boom_script(self):
        s = Script()
        s.add_step(lambda: self._pixels.set_source(explosion_now(self._pixels.size(), stereo=[0, 1])))
        s.add_sleep(6)
        return s
