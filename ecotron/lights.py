from ecotron.color_controller import DEFAULT_COLOR_CONTROLLER
from director import execute, Script
from utils import translate
from value_source import RGB, Concat, GradientDefinition, Max, Sine, ValueSource, repeated_pulse, FadeInOut, Multiply, Constant, Gradient, GradientRandomWalk, ValueSourceWithOverlays
from ecotron.widget import Widget
from enum import Enum
from ecotron.properties import LightMode

def flash_pixels(pixels, duration=1):
    src = pixels.source
    pixels.source = Max(
        repeated_pulse(1, duration),
        src
    )
    execute(Script()
        .add_sleep(duration)
        .add_step(lambda: pixels.set_source(src))
    )


class Lights(Widget):

    def __init__(self, lights, properties, color_control=True):
        Widget.__init__(self)
        self._lights = lights
        self._properties = properties
        self._color_control = color_control
        self._source = LightPropertiesSource(lights.size(), properties)
        self._lights.source = FadeInOut(duration_s=0.5, source=self._source)
        self.bind_to_property(properties.on)

    def when_turn_on(self):
        self._lights.source.fade_in()
        if self._color_control:
            DEFAULT_COLOR_CONTROLLER.set_current_properties(self._properties)

    def when_turn_off(self):
        self._lights.source.fade_out()
        if self._color_control:
           DEFAULT_COLOR_CONTROLLER.set_current_properties(None)

    def set_properties(self, properties):
        self._source.set_properties(properties)

    def add_overlay(self, source):
        self._source.add_overlay(source)

    def size(self):
        return self._lights.size()


class LightPropertiesSource(ValueSource):
    def __init__(self, size, light_properties):
        ValueSource.__init__(self)
        self._size = size
        self._properties = light_properties
        self._inner_source = ValueSourceWithOverlays(source_from_light_properties(self._size, self._properties))
        light_properties.mode.on_value_change = lambda _: self.when_switch_mode()
        light_properties.param.on_value_change = lambda _: self.when_switch_mode()

    def add_overlay(self, source):
        self._inner_source.add_overlay(source)

    def set_properties(self, properties):
        self._properties = properties
        self.when_switch_mode()

    def when_switch_mode(self):
        self._inner_source._inner_source = source_from_light_properties(self._size, self._properties)

    def value(self):
        return self._inner_source.value()

    def _create_inner_source(self):
        return


def source_from_light_properties(size, p):
        mode = p.mode.value()
        if mode == LightMode.CONSTANT:
            return p.color
        elif mode == LightMode.PULSE:
            # 0 = 5s; 1 = 0.3s
            speed = translate(p.param.value(), 0, 1, 5, 0.3)
            return Sine(speed, source=p.color)
        elif mode == LightMode.PLASMA:
            # 0 = 5s; 1 = 0.3s
            speed = translate(p.param.value(), 0, 1, 2, 0.05)
            gradient = GradientDefinition([
                (0, RGB(0, 0, 0)),
                (1, p.color)
            ])
            return Concat(*[
                GradientRandomWalk(gradient, speed=speed)
                for _ in range(size)
            ])
        else:
            raise Exception(f"Unknown light mode: {mode}")
