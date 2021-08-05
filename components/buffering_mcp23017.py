from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp230xx.digital_inout import DigitalInOut, _enable_bit, _clear_bit, _get_bit
from tick_aware import TickAware

class BufferingMcp23017(MCP23017, TickAware):
    
    def __init__(self, i2c, address, reset=True):
        MCP23017.__init__(self, i2c, address=address, reset=reset)
        TickAware.__init__(self)

        self.gpio = 0

        self._gpio_read_buffer = self.gpio
        self._gpio_write_buffer =  self.gpio

    def tick(self, time_s, delta_s):
        if self._gpio_write_buffer != None:
            self.gpio = self._gpio_write_buffer
        self._gpio_read_buffer = self.gpio
        self._gpio_write_buffer = self._gpio_read_buffer

    def get_pin(self, pin):
        assert 0 <= pin <= 15
        return BufferingDigitalInOut(pin, self)
    

class BufferingDigitalInOut(DigitalInOut):
    def __init__(self, pin_number, mcp230xx):
        super().__init__(pin_number, mcp230xx)

    @property
    def value(self):
        return _get_bit(self._mcp._gpio_read_buffer, self._pin)

    @value.setter
    def value(self, val):
        if val:
            self._mcp._gpio_write_buffer = _enable_bit(self._mcp._gpio_write_buffer, self._pin)
            self._mcp._gpio_read_buffer = _enable_bit(self._mcp._gpio_read_buffer, self._pin)
        else:
            self._mcp._gpio_write_buffer = _clear_bit(self._mcp._gpio_write_buffer, self._pin)
            self._mcp._gpio_read_buffer = _clear_bit(self._mcp._gpio_read_buffer, self._pin)
 