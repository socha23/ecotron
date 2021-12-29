import math
import random
import colorsys
from utils import translate
from tick_aware import TickAware, TimeAware

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
        raise Exception(f"Cannot multiply {value} by {multiplier}")


def clamp(value, min_value=0, max_value=1):
    if is_number(value):
        return min(max_value, max(min_value, value))
    elif is_list(value):
        return [clamp(v, min_value, max_value) for v in value]
    elif is_tuple(value):
        return tuple(clamp(list(value), min_value, max_value))
    else:
        raise Exception(f"Cannot clamp {value}")



def add(value, other):
    # scalar add
    if is_number(value) and is_number(other):
        return value + other
    # vector add
    elif is_list(value) and is_list(other):
        return [add(x, other[idx]) for idx, x in enumerate(value)]
    # list x scalar
    elif is_list(value) and is_number(other):
        return [add(x, other) for x in value]
    # scalar x list
    elif is_number(value) and is_list(other):
        return add(other, value)
    # tuple x scalar
    elif is_tuple(value) and is_number(other):
        return tuple(add(list(value), other))
    # scalar x tuple
    elif is_number(value) and is_tuple(other):
        return add(other, value)
    # tuple x list
    elif is_tuple(value) and is_list(other):
        return [add(value, x) for x in other]
    # list x tuple
    elif is_list(value) and is_tuple(other):
        return add(other, value)
    # tuple x tuple
    elif is_tuple(value) and is_tuple(other):
        return tuple(add(list(value), list(other)))
    else:
        raise Exception(f"Cannot add {value} and {other}")


def ultra_max(value, other):
    # scalar max
    if is_number(value) and is_number(other):
        return max(value, other)
    # vector
    elif is_list(value) and is_list(other):
        return [ultra_max(x, other[idx]) for idx, x in enumerate(value)]
    # list x scalar
    elif is_list(value) and is_number(other):
        return [ultra_max(x, other) for x in value]
    # scalar x list
    elif is_number(value) and is_list(other):
        return ultra_max(other, value)
    # tuple x scalar
    elif is_tuple(value) and is_number(other):
        return tuple(ultra_max(list(value), other))
    # scalar x tuple
    elif is_number(value) and is_tuple(other):
        return ultra_max(other, value)
    # tuple x list
    elif is_tuple(value) and is_list(other):
        return [ultra_max(value, x) for x in other]
    # list x tuple
    elif is_list(value) and is_tuple(other):
        return ultra_max(other, value)
    # tuple x tuple
    elif is_tuple(value) and is_tuple(other):
        return tuple(ultra_max(list(value), list(other)))
    else:
        raise Exception(f"Cannot max {value} and {other}")

def ultra_min(value, other):
    # scalar min
    if is_number(value) and is_number(other):
        return min(value, other)
    # vector
    elif is_list(value) and is_list(other):
        return [ultra_min(x, other[idx]) for idx, x in enumerate(value)]
    # list x scalar
    elif is_list(value) and is_number(other):
        return [ultra_min(x, other) for x in value]
    # scalar x list
    elif is_number(value) and is_list(other):
        return ultra_min(other, value)
    # tuple x scalar
    elif is_tuple(value) and is_number(other):
        return tuple(ultra_min(list(value), other))
    # scalar x tuple
    elif is_number(value) and is_tuple(other):
        return ultra_min(other, value)
    # tuple x list
    elif is_tuple(value) and is_list(other):
        return [ultra_min(value, x) for x in other]
    # list x tuple
    elif is_list(value) and is_tuple(other):
        return ultra_min(other, value)
    # tuple x tuple
    elif is_tuple(value) and is_tuple(other):
        return tuple(ultra_min(list(value), list(other)))
    else:
        raise Exception(f"Cannot min {value} and {other}")


class ValueSource(TimeAware):
    def __init__(self):
        TimeAware.__init__(self)

    def value(self):
        return 1


class Constant:
    def __init__(self, val):
        self._val = val

    def value(self):
        return self._val

class Lambda:
    def __init__(self, s):
        self._s = s

    def value(self):
        return self._s()

class RepeatedConstant:
    def __init__(self, val, repeats = 1):
        self._val = [val] * repeats

    def value(self):
        return self._val


class SettableSource:
    def __init__(self, val=0):
        self._value = val

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value



class AlwaysOn(Constant):
    def __init__(self):
        Constant.__init__(self, 1)


class AlwaysOff(Constant):
    def __init__(self):
        Constant.__init__(self, 0)

# COLOR SOURCES

# from byte rgb values
class RGB(Constant):
    def __init__(self, r, g, b):
        Constant.__init__(self, (r / 255, g / 255, b / 255))

class ModifyColor(ValueSource):
    def __init__(self, color_source,
        hue_source = Constant(0),
        saturation_source = Constant(0),
        value_source = Constant(0),
        ):
        ValueSource.__init__(self)
        self._color_source = color_source
        self._hue_source = hue_source
        self._saturation_source = saturation_source
        self._value_source = value_source

    def value(self):
        r, g, b = self._color_source.value()
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        new_h = (h + self._hue_source.value()) % 1
        new_s = clamp((s + self._saturation_source.value()))
        new_v = clamp((v + self._value_source.value()))
        return colorsys.hsv_to_rgb(new_h, new_s, new_v)

class GradientDefinition:
    def __init__(self, definition):
        self._definition = definition

    def _translate(self, current_t, t_from, t_to, val_from, val_to):
        if is_tuple(val_from):
            (r_from, g_from, b_from) = val_from
            (r_to, g_to, b_to) = val_to
            r = translate(current_t, t_from, t_to, r_from, r_to)
            g = translate(current_t, t_from, t_to, g_from, g_to)
            b = translate(current_t, t_from, t_to, b_from, b_to)
            return (r, g, b)
        else:
            return translate(current_t, t_from, t_to, val_from, val_to)


    def __getitem__(self, idx):
        (current_step, current_value) = self._definition[0]

        for (step, value) in self._definition:
            if idx < step:
                return self._translate(idx, current_step, step, current_value.value(), value.value())
            current_step = step
            current_value = value
        return current_value.value()


class Gradient(ValueSource):

    def __init__(self, duration_s, gradient_defition):
        ValueSource.__init__(self)
        self._definition = GradientDefinition(gradient_defition)
        self._time_started = self.current_time()
        self._duration_s = duration_s


    def value(self):
        phase = (self.current_time() - self._time_started) / self._duration_s
        return self._definition[phase]



class GradientRandomWalk(ValueSource):
    def __init__(self, gradient_definition,
            speed=1,
            speed_down = None
    ):
        ValueSource.__init__(self)
        self._speed_up = speed
        self._speed_down = speed_down if speed_down else speed
        self._gradient_definition = gradient_definition
        self._start_point = random.uniform(0, 1)
        self._end_point = self._start_point
        self._start_time = 0
        self._end_time = self.current_time()

    def _next_move(self):
        self._start_point = self._end_point
        self._start_time = self.current_time()
        self._end_point = random.uniform(0, 1)

        speed = self._speed_up if self._end_point > self._start_point else self._speed_down
        self._end_time = self.current_time() + abs(self._start_point - self._end_point) * speed

    def value(self):
        t = self.current_time()
        if t > self._end_time:
            self._next_move()
        if self._start_time == self._end_time:
            return self._gradient_definition[self._start_point]

        v = translate(t,
            self._start_time, self._end_time,
            self._start_point, self._end_point
        )

        return self._gradient_definition[v]


class _Composite(ValueSource):
    def __init__(self, *sources):
        ValueSource.__init__(self)
        self._inner_sources = sources

    def value(self):
        raise "Not implemented"


class _Decorator(ValueSource):
    def __init__(self, source=AlwaysOn()):
        ValueSource.__init__(self)
        self._inner_source = source

    def value(self):
        raise "Not implemented"


class Multiply(_Composite):
    def __init__(self, *factors):
        _Composite.__init__(self, *factors)

    def value(self):
        val = 1
        for s in self._inner_sources:
            val = multiply(val, s.value())
        return val

class Add(_Composite):
    def __init__(self, *factors, min_value=0, max_value=1):
        _Composite.__init__(self, *factors)
        self._min_value=min_value
        self._max_value=max_value

    def value(self):
        val = 0
        for s in self._inner_sources:
            val = add(val, s.value())
        return clamp(val, self._min_value, self._max_value)

class Max(_Composite):
    def __init__(self, *factors):
        _Composite.__init__(self, *factors)

    def value(self):
        val = 0
        for s in self._inner_sources:
            val = ultra_max(val, s.value())
        return val

class Min(_Composite):
    def __init__(self, *factors):
        _Composite.__init__(self, *factors)

    def value(self):
        val = 1
        for s in self._inner_sources:
            val = ultra_min(val, s.value())
        return val

class Concat(_Composite):
    def __init__(self, *factors):
        _Composite.__init__(self, *factors)

    def value(self):
        val = []
        for s in self._inner_sources:
            if is_list(s):
                val += s.value()
            else:
                val.append(s.value())
        return val

class Negative(_Decorator):
    def __init__(self, inner):
        _Decorator.__init__(self, inner)

    def value(self):
        return -self._inner_source.value()

class TimeConstrained(_Decorator):
    def __init__(self, duration_s=1, source=AlwaysOn()):
        _Decorator.__init__(self, source)
        self._cutoff_time = self.current_time() + duration_s

    def value(self):
        if self.current_time() > self._cutoff_time:
            return 0
        else:
            return self._inner_source.value()

class FadeInOut(_Decorator):
    STATE_ON = 1
    STATE_FADE_OUT = 2
    STATE_OFF = 3
    STATE_FADE_IN = 4

    def __init__(self, duration_s=1, source=AlwaysOn()):
        _Decorator.__init__(self, source)
        self._state_transition_on = 0
        self._duration_s = duration_s
        self._state = FadeInOut.STATE_OFF

    def fade_in(self):
        self._state_transition_on = self.current_time()
        self._state = FadeInOut.STATE_FADE_IN

    def fade_out(self):
        self._state_transition_on = self.current_time()
        self._state = FadeInOut.STATE_FADE_OUT


    def value(self):
        if self._state == FadeInOut.STATE_OFF:
            return 0
        elif self._state == FadeInOut.STATE_ON:
            return self._inner_source.value()
        elif self._state == FadeInOut.STATE_FADE_IN:
            phase = (self.current_time() - self._state_transition_on) / self._duration_s
            if phase < 1:
                return multiply(self._inner_source.value(), phase)
            else:
                self._state = FadeInOut.STATE_ON
                return self._inner_source.value()
        else: # self._state == FadeInOut.STATE_FADE_OUT:
            phase = (self.current_time() - self._state_transition_on) / self._duration_s
            if phase < 1:
                return multiply(self._inner_source.value(), 1 - phase)
            else:
                self._state = FadeInOut.STATE_OFF
                return 0


class FadeInFadeOut(ValueSource):

    STATE_ON = 1
    STATE_FADE_OUT = 2
    STATE_OFF = 3
    STATE_FADE_IN = 4

    def __init__(self, duration_s=1, state_on=True):
        ValueSource.__init__(self)
        self._state = FadeInFadeOut.STATE_ON if state_on else FadeInFadeOut.STATE_OFF
        self._transition_start = 0
        self._duration_s = duration_s

    def fade_in(self):
        self._transition_start = self.current_time()
        self._state = FadeInFadeOut.STATE_FADE_IN

    def fade_out(self):
        self._transition_start = self.current_time()
        self._state = FadeInFadeOut.STATE_FADE_OUT

    def value(self):
        if self._state == FadeInFadeOut.STATE_ON:
            return 1
        elif self._state == FadeInFadeOut.STATE_OFF:
            return 0
        else:
            phase = (self.current_time() - self._transition_start) /  self._duration_s
            if self._state == FadeInFadeOut.STATE_FADE_IN:
                if phase > 1:
                    self._state = FadeInFadeOut.STATE_ON
                    return 1
                else:
                    return phase
            else: # self._state == FadeInFadeOut.STATE_FADE_IN:
                if phase > 1:
                    self._state = FadeInFadeOut.STATE_OFF
                    return 0
                else:
                    return 1 - phase

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


class Flicker(_Decorator):
    def __init__(self, amount=1, source=AlwaysOn()):
        _Decorator.__init__(self, source)
        self._last_flick_started = self.current_time()
        self._next_flick_to_start = None
        self._amount = amount

    def value(self):
        FLICK_TIME = 0.04
        FLICK_PAUSE = max(0, (1 - self._amount)) * 2 + 0.5 # between 2.5 and 0.5
        FLICK_REPEAT_CHANCE = 0.8
        FLICK_PAUSE_BETWEEN_REPEATS = 0.04

        t = self.current_time()

        if self._last_flick_started and t <= self._last_flick_started + FLICK_TIME:
            return (0, 0, 0)
        elif self._last_flick_started and t > self._last_flick_started + FLICK_TIME:
            self._last_flick_started = None
            if random.random() < FLICK_REPEAT_CHANCE:
                self._next_flick_to_start = t + FLICK_PAUSE_BETWEEN_REPEATS
            else:
                self._next_flick_to_start = t + random.uniform(0.5, FLICK_PAUSE) + random.uniform(0.5, FLICK_PAUSE)
            return self._inner_source.value()
        elif self._next_flick_to_start and self._next_flick_to_start <= t:
            self._last_flick_started = t
            self._next_flick_to_start = None
            return (0, 0, 0)
        else:
            return self._inner_source.value()



def repeated_blink(how_many=3, duration=1, source=AlwaysOn()):
    return TimeConstrained(how_many * duration, Blink(duration, source))

def repeated_pulse(how_many=3, duration=1, source=AlwaysOn()):
    return TimeConstrained(how_many * duration, Sine(duration, source, common_phase=False))

# sine pulse
class Sine(_Decorator):
    def __init__(self, time_s=1, source=AlwaysOn(), common_phase=False):
        _Decorator.__init__(self, source)
        self._time_s = time_s
        self._phase_start = 0 if common_phase else self.current_time() - (time_s * 0.75)

    def value(self):
        cycle_time = ((self.current_time() - self._phase_start) % self._time_s) / self._time_s
        multiplier = (math.sin(2 * math.pi * cycle_time) + 1) / 2
        val = multiply(self._inner_source.value(), multiplier)
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
        self._current_source = new_source


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

    def set_source(self, new_source):
        self.source = new_source


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


def wave_mask(size, spread, phase, wave_width=2):
    result = []
    for i in range(size):
        i = i % spread
        dist = min(abs(i - phase), abs(i - phase - spread), abs(i - phase + spread))
        result.append(max(0, 1 - dist / wave_width))
    return result




# Eye blink

BLINK_TIME = 0.1

PAUSE_BETWEEN_BLINKS = 4
PAUSE_BETWEEN_MULTIBLINKS = 0.1

CHANCE_FOR_MULTI_BLINK = 0.5

class EyeBlink(ValueSource):
    def __init__(self):
        ValueSource.__init__(self)
        self._blink_start = 0
        self._last_was_doubleblink = False

    def random_pause_between_blinks(self):
        if not self._last_was_doubleblink and random.random() < CHANCE_FOR_MULTI_BLINK:
            self._last_was_doubleblink = True
            return PAUSE_BETWEEN_MULTIBLINKS
        self._last_was_doubleblink = False
        return PAUSE_BETWEEN_BLINKS * (random.random() + random.random())


    def value(self):
        t = self.current_time()
        if t > self._blink_start and t < self._blink_start + BLINK_TIME:
            blink_phase = (t - self._blink_start) / BLINK_TIME
            brightness = abs(blink_phase - 0.5)
            return brightness
        elif t > self._blink_start + BLINK_TIME:
            self._blink_start = t + self.random_pause_between_blinks()
            return 1
        else: # t < self._blink_start
            return 1
