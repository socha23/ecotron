import board
from busio import I2C
from time import sleep
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
from tick_aware import TickAware, DEFAULT_CONTROLLER
from value_source import AlwaysOnSource, AlwaysOffSource, SourceWatcherMixin, Blink

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
        self.on_press = lambda: None
        self.on_release = lambda: None
        self.on_click = lambda _: None

    @property
    def value(self):
        return self._pin.value

    def is_pressed(self):
        return (self._pin.pull == Pull.DOWN) == self.value

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

class PrimitiveLED:
    def __init__(self, pin):        
        self._pin = pin
        pin.direction = Direction.OUTPUT

    @property
    def value(self):
        return 1 if self._pin.value else 0

    @value.setter
    def value(self, val):
        print(f"setting {val}")
        self._pin.value = (val == 1)


class LED(SourceWatcherMixin):
    def __init__(self, pin):
        SourceWatcherMixin.__init__(self)        
        self._primitive_led = PrimitiveLED(pin)

    def on_value_change(self, val):
        self._primitive_led.value = val

    def on(self):
        self.source = AlwaysOnSource()

    def off(self):
        self.source = AlwaysOffSource()

    def blink(self, on_time = 1, off_time = 1):
        self.source = Blink(on_time, off_time)


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


led1 = LED(mcp.get_pin(8))
led2 = LED(mcp.get_pin(10))
led3 = LED(mcp.get_pin(12))



but1 = Button(mcp.get_pin(9))
but2 = Button(mcp.get_pin(11))
but3 = Button(mcp.get_pin(13))

butg = Button(mcp.get_pin(14))
butr = Button(mcp.get_pin(15))

#but1 = ToggleButton(mcp.get_pin(9), mcp.get_pin(8))
#but2 = ToggleButton(mcp.get_pin(11), mcp.get_pin(10))
#but3 = ToggleButton(mcp.get_pin(13), mcp.get_pin(12))


but1.on_press = lambda: print(f"but1")
but2.on_press = lambda: print(f"but2")
but3.on_press = lambda: print(f"but3")

butr.on_press = lambda: print(f"butr")
butg.on_press = lambda: print(f"butg")

DEFAULT_CONTROLLER.on = True

while True:
    led1.blink(0.2, 0.2)
    sleep(1)
    led1.off()
    led2.blink(0.2, 0.2)
    sleep(1)
    led2.off()
    led3.blink(0.2, 0.2)
    sleep(1)
    led3.off()

while True:
    sleep(0.1)
