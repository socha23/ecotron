from ecotron.properties import DEFAULT_ECOTRON_PROPERTIES
from ecotron.lights import Lights
from value_source import AlwaysOff, Sine
from .widget import Widget

OPEN_SPEED = 0.1
CLOSE_SPEED = 0.1

OPEN_ANGLE = 30
CLOSED_ANGLE = 140

def ReactorFanLights(lights):
    color = DEFAULT_ECOTRON_PROPERTIES.reactor_fan_lights_color
    return Lights(lights, color, color_property=color)

class ReactorLights(Widget):
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
