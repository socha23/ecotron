from ecotron.color_controller import DEFAULT_COLOR_CONTROLLER
from director import execute, Script
from typing import Collection
from value_source import RGB, Concat, GradientDefinition, Max, repeated_pulse, FadeInOut, Multiply, Constant, Gradient, GradientRandomWalk
from ecotron.widget import Widget
import gradients

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

    def __init__(self, lights, source, color_property=None, color_controller=DEFAULT_COLOR_CONTROLLER):
        Widget.__init__(self)
        if color_property == None:
            color_property = source
        self._color_property = color_property
        self._source = FadeInOut(duration_s=0.5, source=source)
        self._lights = lights
        self._lights.source = self._source
        self._color_controller=color_controller

    def when_turn_on(self):
        self._source.fade_in()
        if self._color_controller:
            self._color_controller.set_current_property(self._color_property)


    def when_turn_off(self):
        self._source.fade_out()
        if self._color_controller:
            self._color_controller.set_current_property(None)


def floor_lights(lights, color_property, color_controller=None):
#    vs = value_source.Multiply(
#            value_source.Add(
#                value_source.Constant(0.4),
#                value_source.Multiply(value_source.Sine(time_s=3), value_source.Constant(0.6))
#            ),
#            color_property
#        )
    gradient = GradientDefinition([
        (0, RGB(0, 0, 0)),
        (1, color_property)
    ])
    vs = Concat(*[
        GradientRandomWalk(gradient, speed=2)
        for _ in range(lights.size())
    ])
    #gradient = gradients.FIRE
    #vs = Concat(*[
    #    GradientRandomWalk(gradient, speed_down=0.3)
    #    for _ in range(lights.size())
    #])

    return Lights(lights, vs, color_property=color_property, color_controller=color_controller
    )
