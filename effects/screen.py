import glob
from sound import Clip
from director import Script
import value_source
from value_source import RGB
import random


DEFAULT_COLOR_GRADIENT = value_source.GradientDefinition([(0, (1,1,1)), (1, (1,1,1))])


PEACEFUL_SCAN = value_source.GradientDefinition([(0, RGB(0, 168, 157)), (0.5, RGB(0,33,136)), (1, RGB(0,164,200))])


def _short_pause_script(max_duration_s):

    pause_from = min(0.3, max_duration_s)
    pause_to = min(0.7, max_duration_s)

    return Script().add_sleep(random.uniform(pause_from, pause_to))


def _flicker_script(max_duration_s, neopixels, color):
    FLICKER_TIME = 0.1
    FLICKER_TIMES_FROM = 2
    FLICKER_TIMES_TO = 5


    s = Script()
    max_times_left = int(max_duration_s / FLICKER_TIME)
    repeats_from = min(max_times_left, FLICKER_TIMES_FROM)
    repeats_to = min(max_times_left, FLICKER_TIMES_TO)

    (r, g, b) = color

    for _ in range(random.randint(repeats_from, repeats_to)):
        s.add_step(lambda: neopixels.set_source(value_source.Constant(color)))
        s.add_sleep(FLICKER_TIME / 2)
        s.add_step(lambda: neopixels.set_source(value_source.Constant((r/2, g/2, b/2))))
        s.add_sleep(FLICKER_TIME / 2)
    s.add_step(lambda: neopixels.set_source(value_source.Constant(color)))
    return s

def _next_color(current_color, min_distance=0.5):
    color = current_color
    while abs(color - current_color) < min_distance:
        color = random.random()
    return color

def screen_script(neopixels, duration_s=10, gradient_definition=DEFAULT_COLOR_GRADIENT):
    s = Script()

    time_left = duration_s

    color_idx = _next_color(0)
    s.add_step(lambda: neopixels.set_source(value_source.Constant(gradient_definition[color_idx])))
    while time_left > 0:
        effect_script = None
        effect = random.random()
        if effect < 0.5:
            # flicker
            effect_script = _flicker_script(time_left, neopixels, gradient_definition[color_idx])
        else:            
            effect_script = _short_pause_script(time_left)
        
        time_left -= effect_script.duration_s        
        s.add(effect_script)

        if random.random() < 0.8:
            color_idx = _next_color(color_idx)
            s.add_step(lambda: neopixels.set_source(value_source.Constant(gradient_definition[color_idx])))

        if time_left < 0.3:
            s.add_sleep(time_left)
            time_left = 0
    s.add_step(lambda:neopixels.set_source(value_source.AlwaysOff()))
    return s


def peaceful_screen_script(neopixels, duration_s=10):
    return screen_script(neopixels, duration_s, PEACEFUL_SCAN)