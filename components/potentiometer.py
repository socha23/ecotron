from adafruit_mcp3xxx.analog_in import AnalogIn
from tick_aware import TickAware

NOTIFY_TRESHOLD = 0.01

class Potentiometer(TickAware):
    def __init__(self, mcp, mcp_pin):        
        TickAware.__init__(self)
        self._channel = AnalogIn(mcp, mcp_pin)
        self._last_value = None
        self.on_change = lambda _: None

    @property
    def value(self):
        return (65535 - self._channel.value) / 65536

    def tick(self, time, delta):
        val = self.value
        if self._last_value == None or abs(self._last_value - self.value) >= NOTIFY_TRESHOLD:
            self._last_value = val
            if self.on_change != None:
                self.on_change(val)
