from ecotron.widget import Widget
from value_source import repeated_pulse, RGB

class ConveyorReceiver(Widget):

    def __init__(self, neopixel):        
        Widget.__init__(self)
        self._neopixel = neopixel

    def flash_ok(self):
        self._neopixel.source = repeated_pulse(3, 0.5, RGB(0, 16, 0))
