import board
import neopixel
import atexit
from tick_aware import TickAware
from value_source import SourceWatcherMixin, AlwaysOffSource, ConstantSource


class NeopixelStrip(TickAware):

    def __init__(self, pin, pixel_count):
        TickAware.__init__(self)
        self._pixels = neopixel.NeoPixel(pin, pixel_count, auto_write=False)
        self._pixel_count = pixel_count
        self._value = [(0, 0, 0)] * pixel_count
        self._last_value = []
        atexit.register(self.off)

    def tick(self, time_s, delta_s):
        if self._value != self._last_value:
            self._pixels[:] = self._value
            self._pixels.show()
            self._last_value[:] = self._value

    def off(self):
        self._pixels[:] = [(0,0,0)] * self._pixel_count
        self._pixels.show()

    def set(self, offset, values):        
        self._value[offset:(offset + len(values))] = values


class NeopixelSegment(SourceWatcherMixin):

    def __init__(self, strip, offset, pixel_count):
        SourceWatcherMixin.__init__(self)
        self._strip = strip
        self._offset = offset
        self._pixel_count = pixel_count

    def _normalize_value(self, value):
        if isinstance(value, list) and len(value) != self._pixel_count:
            raise f"Wrong number of values in list, expected {self._pixel_count} but got {len(value)}"

        if not isinstance(value, list):
            value = [value] * self._pixel_count
        result = []
        for v in value:
            if not isinstance(v, tuple):
                v = (v, v, v)
            result.append(v)
        return result

    def on_value_change(self, val):
        self._strip.set(self._offset, self._normalize_value(val))

    def off(self):
        self.source = AlwaysOffSource()

    def constant(self, val):
        self.source = ConstantSource(val)

