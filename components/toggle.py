from digitalio import Direction, Pull
from tick_aware import TickAware

class Toggle(TickAware):
    def __init__(self, pin, pull = Pull.UP):
        TickAware.__init__(self)
        self._pin = pin
        pin.direction = Direction.INPUT
        pin.pull = pull
        self._pull = pull
        self.on_on = lambda: None
        self.on_off = lambda: None
        self._last_tick_value = None
        self._properties = []

    def value(self):
        return self._pin.value

    def is_on(self):
        return (self._pull == Pull.DOWN) == self.value()

    def is_off(self):
        return not self.is_on()

    def tick(self, time, delta):
        if self.value() != self._last_tick_value:
            if self.is_on():
                self._on_on()
            else:
                self._on_off()
        self._last_tick_value = self.value()

    def _on_on(self):
        for p in self._properties:
            p.set_value(1)

    def _on_off(self):
        for p in self._properties:
            p.set_value(0)

    def bind_property(self, *properties):
        self._properties = properties

class ToggleBoard:
    def __init__(self, toggles):
        self.toggles = toggles
