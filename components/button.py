from digitalio import Direction, Pull
from tick_aware import TickAware

class Button(TickAware):
    def __init__(self, pin, pull = Pull.UP):
        TickAware.__init__(self)
        self._pin = pin
        pin.direction = Direction.INPUT
        pin.pull = pull
        self._pull = pull
        self._last_pressed_time = 0
        self._last_released_time = 0
        self._last_tick_pressed = False
        self.on_press = lambda: None
        self.on_release = lambda: None
        self.on_click = lambda _: None

    @property
    def value(self):
        return self._pin.value

    def is_pressed(self):
        return (self._pull == Pull.DOWN) == self.value

    def tick(self, time, delta):
        if self.is_pressed() and not self._last_tick_pressed:
            self._on_press(time)
        elif not self.is_pressed() and self._last_tick_pressed:
            self._on_release(time)

    def _on_press(self, time):
        self._last_pressed_time = time
        self._last_tick_pressed = True
        if self.on_press != None:
            self.on_press()

    def _on_release(self, time):
        self._last_released_time = time
        self._last_tick_pressed = False
        if self.on_release != None:
            self.on_release()
        self._on_click(time - self._last_pressed_time)

    def _on_click(self, time):
        if self.on_click != None:
            self.on_click(time)
