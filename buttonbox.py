import board
from busio import I2C
from time import sleep
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
from tick_aware import TickAware

# buttonbox based on MCP23017

mcp = MCP23017(I2C(board.SCL, board.SDA), address=0x20)

class Button(TickAware):
    def __init__(self, pin, pull = Pull.UP):
        TickAware.__init__(self)
        self._pin = pin
        pin.direction = Direction.INPUT
        pin.pull = pull
        self._last_pressed_time = 0
        self._last_released_time = 0
        self._last_tick_pressed = False
        self.on_press = lambda : True
        self.on_release = lambda : True
        self.on_click = lambda time: time

    @property
    def value(self):
        return self._pin.value

    @value.setter
    def value(self, val):
        self._pin.value = val

    def is_pressed(self):
        return (self._pin.pull == Pull.DOWN) == self._pin.value

    def tick(self, time, delta):
        if self.is_pressed() and not self._last_tick_pressed:
            self._on_press(time)
        elif not self.is_pressed() and self._last_tick_pressed:
            self._on_release(time)

    def _on_press(self, time):
        self._last_pressed_time = time
        self._last_tick_pressed = True
        self.on_press()

    def _on_release(self, time):
        self._last_released_time = time
        self._last_tick_pressed = False
        self.on_release()
        self._on_click(time - self._last_pressed_time)

    def _on_click(self, time):
        self.on_click(time)

class LED:
    def __init__(self, pin):
        self._pin = pin
        pin.direction = Direction.OUTPUT

    @property
    def value(self):
        return self._pin.value

    @value.setter
    def value(self, val):
        self._pin.value = val


class ToggleButton(Button):
    
    def __init__(self, pin, pull = Pull.UP):
        Button.__init__(self, pin, pull)
        self._on = False
        self.on_toggle = lambda on: True

    def _on_click(self, time):
        self._on = not self._on
        self._on_toggle(self._on)
        Button._on_click(self, time)

    def _on_toggle(self, is_on):
        self.on_toggle(is_on)  

    def is_on(self):
        return self._on


class LedToggleButton(ToggleButton):
    
    def __init__(self, button_pin, led_pin, pull = Pull.UP):
        ToggleButton.__init__(self, button_pin, pull)
        self.led = LED(led_pin)

    def _on_toggle(self, is_on):
        self.led.value = is_on
        ToggleButton._on_toggle(self, is_on)


red = LedToggleButton(mcp.get_pin(3), mcp.get_pin(0))
yellow = LedToggleButton(mcp.get_pin(5), mcp.get_pin(1))

red.on_toggle = lambda s: print(f"red: {s}")
yellow.on_toggle = lambda s: print(f"yellow: {s}")


while True:
    sleep(0.1)
