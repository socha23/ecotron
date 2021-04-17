import math
import random

from tick_aware import TickAware

def is_number(val):
    return isinstance(val, int) or isinstance(val, float)

def is_tuple(val):
    return isinstance(val, tuple)

def is_list(val):
    return isinstance(val, list)

def multiply(value, multiplier):
    # scalar multiply
    if is_number(value) and is_number(multiplier):
        return value * multiplier    
    # vector multiply
    elif is_list(value) and is_list(multiplier):
        return [multiply(x, multiplier[idx]) for idx, x in enumerate(value)]
    # list x scalar
    elif is_list(value) and is_number(multiplier):
        return [multiply(x, multiplier) for x in value]
    # scalar x list
    elif is_number(value) and is_list(multiplier):
        return multiply(multiplier, value)
    # tuple x scalar
    elif is_tuple(value) and is_number(multiplier):
        return tuple(multiply(list(value), multiplier))
    # scalar x tuple
    elif is_number(value) and is_tuple(multiplier):
        return multiply(multiplier, value)
    # tuple x list
    elif is_tuple(value) and is_list(multiplier):
        return [multiply(value, x) for x in multiplier]
    # list x tuple
    elif is_list(value) and is_tuple(multiplier):
        return multiply(multiplier, value)
    else:
        raise f"Cannot multiply {value} by {multiplier}"
        
class ValueSource(TickAware):
    def __init__(self):
        TickAware.__init__(self)

    def value(self):
        return 1

    def tick(self, cur_s, delta_s):
        pass

    def close(self):
        TickAware.close(self)


class Constant:
    def __init__(self, val):
        self._val = val

    def value(self):
        return self._val

    def close(self):
        pass


class AlwaysOn(Constant):
    def __init__(self):
        Constant.__init__(self, 1)


class AlwaysOff(Constant):
    def __init__(self):
        Constant.__init__(self, 0)


# from byte rgb values
class RGB(Constant):
    def __init__(self, r, g, b):
        Constant.__init__(self, (r / 255, g / 255, b / 255))


class _Composite(ValueSource):
    def __init__(self, *sources):
        ValueSource.__init__(self)
        self._inner_sources = sources

    def value(self):
        raise "Not implemented"

    def close(self):
        ValueSource.close(self)
        for s in self._inner_sources:
            s.close()


class _Decorator(ValueSource):
    def __init__(self, source=AlwaysOn()):
        ValueSource.__init__(self)
        self._inner_source = source

    def value(self):
        raise "Not implemented"

    def close(self):        
        ValueSource.close(self)
        self._inner_source.close()


class Multiply(_Composite):
    def __init__(self, *factors):
        _Composite.__init__(self, *factors)

    def value(self):
        val = 1
        for s in self._inner_sources:
            val = multiply(val, s.value())
        return val

class TimeConstrained(_Decorator):
    def __init__(self, duration_s=1, source=AlwaysOn()):
        _Decorator.__init__(self, source)
        self._cutoff_time = self.current_time() + duration_s

    def value(self):
        if self.current_time() > self._cutoff_time:
            return 0
        else:
            return self._inner_source.value()

class Blink(_Decorator):
    def __init__(self, duration=1, source=AlwaysOn()):
        _Decorator.__init__(self, source)

        if is_number(duration):
            time_on = duration / 2
            time_off = duration / 2
        elif isinstance(duration, list) or isinstance(duration, tuple):
            time_on = duration[0]
            time_off = duration[1]
        else:
            raise "Duration needs to be a numer or a pair"
        self._time_started = self.current_time()        
        self._time_on = time_on
        self._time_off = time_off

    def value(self):
        cycle_time = (self.current_time() - self._time_started) % (self._time_on + self._time_off)
        if cycle_time < self._time_on:
            return self._inner_source.value()
        else:
            return 0


def repeated_blink(how_many=3, duration=1, source=AlwaysOn()):
    return TimeConstrained(how_many * duration, Blink(duration, source))


# sine pulse
class Sine(_Decorator):
    def __init__(self, time_s=1, source=AlwaysOn(), common_phase=True):
        _Decorator.__init__(self, source)
        self._time_s = time_s
        self._phase_start = 0 if common_phase else self.current_time() - (time_s * 0.75)

    def value(self):
        cycle_time = ((self.current_time() - self._phase_start) % self._time_s) / self._time_s
        multiplier = (math.sin(2 * math.pi * cycle_time) + 1) / 2
        val = multiply(self._inner_source.value(), multiplier)
        print(f"cycle time: {cycle_time}, val {val}")
        return  val


class SourceWatcher(TickAware):
    def __init__(self, on_change=lambda x: None):
        self._current_source = AlwaysOff()
        TickAware.__init__(self)
        self._last_val = None
        self._on_change = on_change

    def tick(self, cur_s, delta_s):
        new_val = self._current_source.value()
        if self._last_val != new_val:
            self._last_val = new_val
            if self._on_change != None:
                self._on_change(new_val)

    @property
    def source(self):
        return self._current_source

    @source.setter
    def source(self, new_source):
        if self._current_source != None:
            self._current_source.close()
        self._current_source = new_source

    def close(self):
        if self._current_source != None:
            self._current_source.close()


class SourceWatcherMixin:
    def __init__(self):
        self._source_watcher = SourceWatcher(self.on_value_change)

    def on_value_change(self, value):
        raise "Not implemented"

    @property 
    def source(self):
        return self._source_watcher.source

    @source.setter
    def source(self, new_source):
        self._source_watcher.source = new_source


# deprecated
class MultiplySource(ValueSource):
    def __init__(self, inner_source, multiplier=1):
        ValueSource.__init__(self)
        self._inner_source = inner_source
        self._multiplier = multiplier

    def value(self):
        return self._inner_source.value() * self._multiplier

    def close(self):
        self._inner_source.close()
        ValueSource.close(self)



# pixel strip only - running 'wave', left-to-right
class Wave(ValueSource):
    def __init__(self, size, inner_source=AlwaysOn(), pixels_per_s=1, wave_width=4, spread=10, phase=0):
        ValueSource.__init__(self)
        self._size = size
        self._inner_source = inner_source
        self._wave_width = wave_width
        self._pixels_per_s = pixels_per_s
        self._spread = spread
        self._phase = phase

    def value(self):
        current_phase = (self.current_time() * self._pixels_per_s + self._phase) % self._spread
        mask = wave_mask(self._size, self._spread, current_phase, wave_width=self._wave_width)
        return multiply(self._inner_source.value(), mask)
        
    def close(self):
        self._inner_source.close()
        ValueSource.close(self)


def wave_mask(size, spread, phase, wave_width=2):
    result = []
    for i in range(size):
        i = i % spread
        dist = min(abs(i - phase), abs(i - phase - spread), abs(i - phase + spread))
        result.append(max(0, 1 - dist / wave_width))
    return result

