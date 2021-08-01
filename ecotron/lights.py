import value_source
from ecotron.widget import Widget

class Lights(Widget):

    def __init__(self, lights, source):
        Widget.__init__(self)

        self._source = value_source.FadeInOut(duration_s=0.5, source=source)
        self._lights = lights
        self._lights.source = self._source

    def when_turn_on(self):
        self._source.fade_in()

    def when_turn_off(self):
        self._source.fade_out()


def floor_lights(lights, color):
    return Lights(lights, value_source.Multiply(
#            value_source.Wave(base.floor_light.size(), pixels_per_s=10, inner_source=value_source.RGB(32, 32, 20)),
            
            # brightness - sine from 0.4 to 1
            value_source.Add(
                value_source.Constant(0.4), 
                value_source.Multiply(value_source.Sine(time_s=3), value_source.Constant(0.6))
            ),            
            color
        )
    )
