from typing import Collection
import value_source
from ecotron.widget import Widget

class Lights(Widget):

    def __init__(self, lights, source, color_property=None, color_controller=None):
        Widget.__init__(self)
        if color_property == None:
            color_property = source
        self._color_property = color_property
        self._source = value_source.FadeInOut(duration_s=0.5, source=source)
        self._lights = lights
        self._lights.source = self._source
        self._color_controller=color_controller

    def when_turn_on(self):
        self._source.fade_in()
        if self._color_controller:
            self._color_controller.set_current_property(self._color_property)


    def when_turn_off(self):
        self._source.fade_out()
        self._color_controller.set_current_property(None)


def floor_lights(lights, color_property, color_controller=None):
    return Lights(lights, value_source.Multiply(

#            value_source.Wave(base.floor_light.size(), pixels_per_s=10, inner_source=value_source.RGB(32, 32, 20)),
            
            # brightness - sine from 0.4 to 1
            value_source.Add(
                value_source.Constant(0.4), 
                value_source.Multiply(value_source.Sine(time_s=3), value_source.Constant(0.6))
            ),            
            color_property
        ), color_property=color_property, color_controller=color_controller
    )
