import math

from tick_aware import TickAware

class ValueSource(TickAware):
    def __init__(self):
        TickAware.__init__(self)

    def value(self):
        return 1

    def tick(self, cur_s, delta_s):
        pass

    def close(self):
        TickAware.close(self)


class ConstantSource(ValueSource):
    def __init__(self, val):
        ValueSource.__init__(self)
        self._val = val

    def value(self):
        return self._val


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



class AlwaysOnSource(ConstantSource):
    def __init__(self):
        ConstantSource.__init__(self, 1)


class AlwaysOffSource(ConstantSource):
    def __init__(self):
        ConstantSource.__init__(self, 0)


class SourceWatcher(TickAware):
    def __init__(self, on_change=lambda x: None):
        self._current_source = AlwaysOffSource()
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


class Blink(ValueSource):
    def __init__(self, value = 1):
        ValueSource.__init__(self)

        time_on = value
        time_off = value
        if isinstance(value, list) or isinstance(value, tuple):
            time_on = value[0]
            time_off = value[1]
        
        self._time_on = time_on
        self._time_off = time_off

    def value(self):
        cycle_time = self.current_time() % (self._time_on + self._time_off)
        if cycle_time < self._time_on:
            return 1
        else:
            return 0

# sine pulse
class Pulse(ValueSource):
    def __init__(self, time_s=1, inner_source=AlwaysOnSource(), common_phase=True):
        ValueSource.__init__(self)
        self._inner_source = inner_source
        self._time_s = time_s
        self._phase_start = 0 if common_phase else self.current_time()

    def value(self):
        cycle_time = (self.current_time() - self._phase_start) % self._time_s
        multiplier = (math.sin(2 * math.pi * (cycle_time / self._time_s)) + 1) / 2
        return multiply(self._inner_source.value(), multiplier)

    def close(self):
        self._inner_source.close()
        ValueSource.close(self)


# pixel strip only - running 'wave', left-to-right
class Wave(ValueSource):
    def __init__(self, size, inner_source=AlwaysOnSource(), pixels_per_s=1, wave_width=4, spread=10, phase=0):
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