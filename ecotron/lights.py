import value_source
from ecotron.widget import Widget

class Lights(Widget):

    def __init__(self, lights, source):
        Widget.__init__(self)

        self._lights = lights
        self._source = source

    def when_turn_on(self):
        self._lights.source = self._source

    def when_turn_off(self):
        self._lights.source = value_source.AlwaysOff()


def floor_lights(lights):
    return Lights(lights, value_source.Multiply(

#            value_source.Wave(base.floor_light.size(), pixels_per_s=10, inner_source=value_source.RGB(32, 32, 20)),
            
            # brightness - sine from 0.1 to 1
            value_source.Add(
                value_source.Constant(0.4), 
                value_source.Multiply(value_source.Sine(time_s=3), value_source.Constant(0.6))
            ),
            
            # color
            value_source.RGB(10, 60, 50)
        )
    )


def door_lights(lights):
    return Lights(lights, value_source.RGB(20, 30, 60))

def top_lights_floor_1(lights):
    return Lights(lights, value_source.RGB(60, 50, 20))