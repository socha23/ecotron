from director import DEFAULT_DIRECTOR, Script
from .properties import DEFAULT_ECOTRON_PROPERTIES
from .lights import Lights
from value_source import AlwaysOff, Sine, repeated_pulse
from .widget import Widget
from sound import Clip

OPEN_SPEED = 0.1
CLOSE_SPEED = 0.1

OPEN_ANGLE = 30
CLOSED_ANGLE = 140

class ReactorDoor(Widget):
    def __init__(self, door_servo):
        Widget.__init__(self)
        self._door_servo = door_servo
        self.close()

    def when_turn_on(self):
        self.open()

    def when_turn_off(self):
        self.close()

    def open(self):
        self._door_servo.move_to(OPEN_ANGLE, OPEN_SPEED)

    def close(self):
        self._door_servo.move_to(CLOSED_ANGLE, CLOSE_SPEED)


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


def ReactorFanLights(lights):
    color = DEFAULT_ECOTRON_PROPERTIES.reactor_fan_lights_color
    return Lights(lights, color, color_property=color)


CLIP_BOOM = Clip("./resources/explosion_large_1.ogg", stereo=[0, 1])


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
        s.add_step(lambda: CLIP_BOOM.play())
        s.add_sleep(0.4)
        s.add_step(lambda: self._pixels.set_source(repeated_pulse(1, 0.1)))
        s.add_sleep(1)
        return s
