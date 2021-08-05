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
        if self.on_on != None:
            self.on_on()

    def _on_off(self):
        if self.on_off != None:
            self.on_off()

    def bind_property(self, property):
        self.on_on = lambda: property.set_value(1)
        self.on_off = lambda: property.set_value(0)

class ToggleBoard:
    def __init__(self, toggles):
        self.toggles = toggles