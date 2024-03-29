from digitalio import Direction
from value_source import AlwaysOn, AlwaysOff, SourceWatcherMixin, Blink

class PrimitiveLED:
    def __init__(self, pin):
        self._pin = pin
        pin.direction = Direction.OUTPUT

    @property
    def value(self):
        return 1 if self._pin.value else 0

    @value.setter
    def value(self, val):
        self._pin.value = (val == 1)


class LED(SourceWatcherMixin):
    def __init__(self, pin):
        SourceWatcherMixin.__init__(self)
        self._primitive_led = PrimitiveLED(pin)

    def on_value_change(self, val):
        self._primitive_led.value = val

    def on(self):
        self.source = AlwaysOn()

    def off(self):
        self.source = AlwaysOff()

    def blink(self, value = 1):
        self.source = Blink(value)


class PWMLED(SourceWatcherMixin):
    def __init__(self, pwm_channel):
        SourceWatcherMixin.__init__(self)
        self._pwm_channel = pwm_channel

    def on_value_change(self, val):
        val = max(0, min(val, 1))
        self._pwm_channel.duty_cycle = int(0xffff * val**3) # val^2 to correct for non-linearity


