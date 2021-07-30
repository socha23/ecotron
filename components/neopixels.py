import board
import neopixel
import atexit
from tick_aware import TickAware
from value_source import SourceWatcherMixin, AlwaysOff, Constant


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
        self._value[offset:(offset + len(values))] = [(int(r * 255), int(g * 255), int(b * 255)) for (r, g, b) in values]

class Neopixels:
    def __init__(self, strip, offset, pixel_count, reversed=False):
        self._reversed = reversed
        self._strip = strip
        self._offset = offset
        self._pixel_count = pixel_count

    def _normalize_value(self, value):
        if isinstance(value, list) and len(value) != self._pixel_count:
            raise Exception(f"Wrong number of values in list, expected {self._pixel_count} but got {len(value)}")

        if not isinstance(value, list):
            value = [value] * self._pixel_count
        result = []
        for v in value:
            if not isinstance(v, tuple):
                v = (v, v, v)
            result.append(v)

        if self._reversed:
            result.reverse()
        
        return result

    def size(self):
        return self._pixel_count

    def set(self, value):
        self._strip.set(self._offset, self._normalize_value(value))


class FakeNeopixels:
    def __init__(self, pixel_count):
        self._pixel_count = pixel_count

    def set(self, value):
        pass

    def size(self):
        return self._pixel_count


class NeopixelSegment(SourceWatcherMixin):

    def __init__(self, strip, offset, pixel_count):
        SourceWatcherMixin.__init__(self)
        self._neopixels = Neopixels(strip, offset, pixel_count)

    def on_value_change(self, val):
        self._neopixels.set(val)

    def off(self):
        self.source = AlwaysOff()

    def constant(self, val):
        self.source = Constant(val)

    def size(self):
        return self._neopixels.size()


class NeopixelMultiSegment(SourceWatcherMixin):

    def __init__(self, *neopixels):
        SourceWatcherMixin.__init__(self)
        self._neopixels = neopixels
        self._pixel_count = sum([p.size() for p in neopixels])


    def _normalize_value(self, value):
        if isinstance(value, list) and len(value) != self._pixel_count:
            raise Exception(f"Wrong number of values in list, expected {self._pixel_count} but got {len(value)}")
        if not isinstance(value, list):
            value = [value] * self._pixel_count
        return value

    def on_value_change(self, val):
        val = self._normalize_value(val)
        offset = 0
        for pixels in self._neopixels:
            pixels.set(val[offset:offset + pixels.size()])
            offset += pixels.size()

    def off(self):
        self.source = AlwaysOff()

    def constant(self, val):
        self.source = Constant(val)

    def size(self):
        return self._pixel_count


