import board
import busio
from time import sleep
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
from tick_aware import TickAware

i2c = busio.I2C(board.SCL, board.SDA)

mcp = MCP23017(i2c, address=0x20)

class LED:
    def __init__(self, pin):
        self._pin = pin
        pin.direction = Direction.OUTPUT
        pin.value = False
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val:
            self._value = 1
            self._pin.value = True
        else:
            self._value = 0
            self._pin.value = False    

PWM_CYCLE_S = 0.039

class PWM(TickAware):

    def __init__(self, component):
        TickAware.__init__(self)
        self._component = component
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val == 0:
            self._component.value = 0
        self._value = val

    def tick(self, time_s, delta_s):
        phase = (time_s % PWM_CYCLE_S) / PWM_CYCLE_S
        if phase < self.value:
            self._component.value = 1
        else:
            self._component.value = 0

class ConsoleOut(TickAware):
    def __init__(self):
        TickAware.__init__(self)

    def tick(self, time_s, delta_s):
        print(time_s)


pins = [PWM(LED(mcp.get_pin(num))) for num in range(6)]

#for num in range(6):    
#    pins[num].value = (1.0 / 6) * (num + 1)
for pin in pins:
    pin.value = 0.1

sleep(5)

for pin in pins:
    pin.value = 0
